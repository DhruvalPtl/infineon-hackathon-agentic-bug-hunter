# 🐞 Agentic Bug Hunter

> Built at the **Infineon Technologies Hackathon** hosted at **Nirma University**

An intelligent multi-agent system that automatically detects and fixes bugs in Infineon **SmartRDI** C++ code. The system uses a pipeline of specialized AI agents backed by a vector-search knowledge base of official documentation.

---

## 🏆 Hackathon

| | |
|---|---|
| **Event** | Agentic AI Hackathon |
| **Organizer** | Infineon Technologies |
| **Venue** | Nirma University |
| **Track** | Agentic Bug Hunter |

---

## 🏗️ Architecture

```
Input C++ Code (samples.csv)
         │
         ▼
┌─────────────────────┐
│  DRA – Retrieval    │  Searches official Infineon SmartRDI docs
│       Agent         │  via MCP vector database
└────────┬────────────┘
         │ documentation context
         ▼
┌─────────────────────┐
│  DAA – Analysis     │  Diagnoses the exact bug line and reason
│       Agent         │
└────────┬────────────┘
         │ diagnostic report
         ▼
┌─────────────────────┐
│  Correction Agent   │  Writes the corrected C++ code
└────────┬────────────┘
         │ corrected code
         ▼
┌─────────────────────┐
│  QAV – Validator    │  Validates and formats the final JSON report
└────────┬────────────┘
         │
         ▼
  output.csv + Streamlit Dashboard
```

### Agents

| Agent | Role |
|---|---|
| **DRA** – Documentation Retrieval Agent | Queries the MCP server to fetch relevant SmartRDI API rules |
| **DAA** – Diagnostic Analysis Agent | Identifies the exact buggy line with reasoning |
| **Correction Agent** | Rewrites the corrected C++ code |
| **QAV** – Quality Assurance Validator | Verifies and produces a structured JSON report |

### LLM

- **Cloud:** `Qwen/Qwen2.5-7B-Instruct` via HuggingFace Inference API
- **Local (optional):** any model served via [LM Studio](https://lmstudio.ai/) on `localhost:1234`

---

## 📂 Project Structure

```
├── bug_hunter.py        # ✍️  Our work – main multi-agent pipeline
├── app.py               # ✍️  Our work – Streamlit dashboard
├── demo2.py             # ✍️  Our work – quick demo / proof-of-concept agent
├── samples.csv          # 🔷 Provided by Infineon – buggy C++ test cases
├── output.csv           # Auto-generated output (not committed)
├── .env.example         # Environment variables template
├── requirements.txt
└── server/              # 🔷 Provided by Infineon
    ├── mcp_server.py        # FastMCP server exposing `search_documents`
    ├── embedding_model/     # BAAI/bge-base-en-v1.5 config files
    │                        # (.bin / .safetensors / .onnx excluded from repo)
    └── storage/             # Pre-built LlamaIndex vector store of SmartRDI docs
```

> **🔷 Infineon-provided assets** – The `server/` directory (MCP server, pre-built vector store
> of SmartRDI documentation, and embedding model config) along with `samples.csv` (buggy C++
> test cases) were supplied by Infineon Technologies as part of the hackathon challenge kit.
> Model binary weights (`.bin`, `.safetensors`, `.onnx`) are excluded from this repository.

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/DhruvalPtl/infineon-hackathon-agentic-bug-hunter.git
cd infineon-hackathon-agentic-bug-hunter
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your HuggingFace API key
```

Get your free API key at <https://huggingface.co/settings/tokens>.

### 5. Start the MCP server

```bash
python server/mcp_server.py
```

The server will start on `http://localhost:8003/sse`.

### 6. Run the bug hunter

```bash
python bug_hunter.py
```

Results are saved to `output.csv`.

### 7. Launch the dashboard

```bash
streamlit run app.py
```

---

## 🛠️ Local LLM (Optional)

To run fully offline with [LM Studio](https://lmstudio.ai/):

1. Download any GGUF model in LM Studio.
2. Start the local server on `localhost:1234`.
3. In `bug_hunter.py`, set `USE_LOCAL_LLM = True`.

---

## 📊 Input / Output Format

**`samples.csv`** – one buggy C++ snippet per row:

| Column | Description |
|---|---|
| `ID` | Unique identifier |
| `Context` | What the code is supposed to do |
| `Code` | Buggy C++ source code |

**`output.csv`** – generated bug report per row:

| Column | Description |
|---|---|
| `ID` | Links back to `samples.csv` |
| `Bug Line` | Line number of the detected bug |
| `Explanation` | Why it violates the SmartRDI documentation |
| `Corrected Code` | Fixed C++ code |

---

## 🧰 Tech Stack

- [pydantic-ai](https://ai.pydantic.dev/) – Multi-agent orchestration
- [FastMCP](https://github.com/jlowin/fastmcp) – MCP server framework
- [LlamaIndex](https://www.llamaindex.ai/) – Vector index & retrieval
- [HuggingFace](https://huggingface.co/) – LLM inference
- [Streamlit](https://streamlit.io/) – Dashboard
- [python-dotenv](https://github.com/theskumar/python-dotenv) – Environment management

---

## 👥 Team

Built with ❤️ at the Infineon Technologies Hackathon, Nirma University.

| | GitHub |
|---|---|
| Dhruval Patel | [@DhruvalPtl](https://github.com/DhruvalPtl) |
| KN Bhatt | [@knbhatt](https://github.com/knbhatt) |
| Kinjal Rathod | [@kinjal-rathod-14] (https://github.com/kinjal-rathod-14)|
| Team Member 4 | — |

---

## 🙏 Credits

- **Infineon Technologies** – for organising the hackathon, providing the SmartRDI documentation
  vector store, the MCP server scaffold, and the test dataset (`samples.csv`)
- **Nirma University** – for hosting the event
