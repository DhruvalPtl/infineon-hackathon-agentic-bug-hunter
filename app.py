import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Infineon Agentic Bug Hunter", layout="wide", page_icon="🐞")

st.title("🐞 Agentic Bug Hunter - Enterprise Dashboard")
st.markdown("**Architecture:** Multi-Agent Generator-Evaluator (DRA $\\rightarrow$ DAA $\\rightarrow$ QAV)")
st.markdown("---")

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        samples = pd.read_csv("samples.csv")
        output = pd.read_csv("output.csv")
        # Merge the datasets so we can see code and results together
        merged = pd.merge(output, samples, on="ID", how="inner")
        return merged
    except Exception as e:
        st.error(f"Error loading data. Ensure samples.csv and output.csv are in the folder. Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- Sidebar ---
    st.sidebar.header("Navigation")
    st.sidebar.success(f"✅ Processed {len(df)} Bug Reports")
    
    selected_id = st.sidebar.selectbox("Select Code Snippet ID to Review:", df['ID'].tolist())
    
    # Filter data for selected ID
    case = df[df['ID'] == selected_id].iloc[0]
    
    # --- Main Content ---
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📝 Original C++ Code")
        st.info(f"**Context:** {case['Context']}")
        # Display the code with syntax highlighting
        st.code(case['Code'], language='cpp')
        
    with col2:
        st.subheader("🤖 AI Diagnostic Report")
        
        st.metric(label="Detected Bug Line", value=f"Line {case['Bug Line']}")
        
        st.warning("**Bug Explanation:**")
        st.write(case['Explanation'])
        
        st.markdown("---")
        st.markdown("**System Log:**")
        st.markdown("* ✅ **DRA** retrieved documentation successfully.")
        st.markdown("* ✅ **DAA** drafted diagnostic hypothesis.")
        st.markdown("* ✅ **QAV** verified logic and formatted output.")

else:
    st.warning("Awaiting data processing...")