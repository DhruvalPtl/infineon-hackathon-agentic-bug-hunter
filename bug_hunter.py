import asyncio
import os
import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerSSE
from loguru import logger
import sys


USE_LOCAL_LLM = False 

if USE_LOCAL_LLM:
    from pydantic_ai.providers.openai import OpenAIProvider
    from pydantic_ai.models.openai import OpenAIModel
    provider = OpenAIProvider(base_url="http://localhost:1234/v1", api_key="lm-studio")
    model = OpenAIModel("local-model", provider=provider) 
    logger.info("Initialized Secure Local Environment via LM Studio")
else:
    from pydantic_ai.providers.huggingface import HuggingFaceProvider
    from pydantic_ai.models.huggingface import HuggingFaceModel
    provider = HuggingFaceProvider(api_key="REDACTED_HF_KEY") 
    model = HuggingFaceModel("Qwen/Qwen2.5-7B-Instruct", provider=provider)
    logger.info("Initialized Cloud Environment")

class BugReport(BaseModel):
    bug_line: int
    explanation: str
    corrected_code: str

logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

mcp_server = MCPServerSSE('http://localhost:8003/sse')

# AGENT 1: The Retrieval Agent (Connects to MCP Database)
Retrieval_Agent = Agent(
    model, 
    system_prompt=(
        "You are an expert technical researcher for Infineon SmartRDI. "
        "Search the official documentation and return exact usage rules, constraints, "
        "and correct syntax for the queried C++ functions."
    ),
    mcp_servers=[mcp_server]
)

# AGENT 2: The Analysis Agent (Diagnoses the Bug)
Analysis_Agent = Agent(
    model, 
    system_prompt=(
        "You are a Senior C++ Diagnostic Engineer. Look at the buggy code and context. "
        "STEP 1: Identify key SmartRDI functions. "
        "STEP 2: Use the `ask_retrieval` tool to get the official rules for those functions. "
        "STEP 3: Write a highly detailed draft report. Identify the exact line number of the bug "
        "and explain exactly why it violates the documentation."
    )
)

# AGENT 3: The Correction Agent (Generates the Fix)
Correction_Agent = Agent(
    model,
    system_prompt=(
        "You are a C++ Remediation Specialist. You will receive a snippet of buggy C++ code "
        "and a 'Diagnostic Report' explaining what the bug is. "
        "Your ONLY job is to write the corrected C++ code block. "
        "Fix the bug identified in the report without changing the overall logic. "
        "Provide clean, formatted C++ code."
    )
)

# AGENT 4: The QA Validator (Formats the JSON)
Validator = Agent(
    model,
    output_type=BugReport,
    retries=3,
    system_prompt=(
        "You are the Quality Assurance Lead. You will receive: "
        "1. Original Buggy Code\n2. Diagnostic Report\n3. Proposed Corrected Code. "
        "Your job is to combine these into the final official report. "
        "CRITICAL: You must output ONLY valid JSON containing 'bug_line' (integer), "
        "'explanation' (string), and 'corrected_code' (string)."
    )
)

research_cache = {}

@Analysis_Agent.tool
async def ask_retrieval(ctx: RunContext[None], search_query: str) -> str:
    """Delegates a query to the Retrieval Agent to access the search_documents MCP tool."""
    if search_query in research_cache:
        logger.info(f"   [CACHE HIT] Instant reply for: {search_query}")
        return research_cache[search_query]

    logger.info(f"   [RESEARCHING] Querying MCP Database for: {search_query}")
    research_result = await Retrieval_Agent.run(search_query)
    
    research_cache[search_query] = research_result.output 
    return research_result.output 


async def main():
    logger.info("Connecting Agents to MCP Server...")
    
    async with Retrieval_Agent.run_mcp_servers():
        logger.info("Loading samples.csv...")
        try:
            df = pd.read_csv('samples.csv')
        except FileNotFoundError:
            logger.error("Could not find samples.csv.")
            return

        results = []
        processed_ids = set()
        
        if os.path.exists("output.csv"):
            try:
                existing_df = pd.read_csv("output.csv")
                processed_ids = set(existing_df['ID'].tolist())
                results = existing_df.to_dict('records')
                logger.info(f"Resuming progress. Skipping {len(processed_ids)} files...")
            except Exception as e:
                logger.warning(f"Could not read existing output.csv: {e}")

        for index, row in df.iterrows():
            code_id = row['ID']
            if code_id in processed_ids:
                continue
                
            context = row['Context']
            buggy_code = row['Code']

            logger.info(f"\n--- Analyzing Code ID: {code_id} ---")
            
            try:
                
                logger.info("Phase 1: Analysis Agent is diagnosing the bug...")
                analysis_prompt = f"Context: {context}\n\nBuggy Code:\n{buggy_code}\n\nFind the bug."
                analysis_draft = await Analysis_Agent.run(analysis_prompt)
               
                logger.info("Phase 2: Correction Agent is writing the fix...")
                correction_prompt = f"Buggy Code:\n{buggy_code}\n\nDiagnostic Report:\n{analysis_draft.output}\n\nWrite the corrected C++ code."
                correction_draft = await Correction_Agent.run(correction_prompt)
                
                logger.info("Phase 3: QA Validator is formatting the official JSON report...")
                validator_prompt = (
                    f"Buggy Code:\n{buggy_code}\n\n"
                    f"Diagnostic Report:\n{analysis_draft.output}\n\n"
                    f"Proposed Fix:\n{correction_draft.output}\n\n"
                    "Compile this into the final JSON output."
                )
                final_result = await Validator.run(validator_prompt)
                
                logger.info(f"VERIFIED SUCCESS -> Line {final_result.output.bug_line} fixed.")
            
                results.append({
                    "ID": code_id,
                    "Bug Line": final_result.output.bug_line,
                    "Explanation": final_result.output.explanation,
                    "Corrected Code": final_result.output.corrected_code
                })
                
                pd.DataFrame(results).to_csv("output.csv", index=False)
                await asyncio.sleep(2) 
                
            except Exception as e:
                logger.error(f"Error processing ID {code_id}: {e}")
        
        logger.info("\nFinal results saved to output.csv!")

if __name__ == "__main__":
    asyncio.run(main())