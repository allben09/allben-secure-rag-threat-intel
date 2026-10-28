"""
src/app.py
Streamlit UI for Secure RAG Threat Intelligence.
"""
import streamlit as st
import os
from guardrails import check_prompt_injection, redact_pii
from rag_engine import setup_database, secure_retrieval, generate_secure_response

st.set_page_config(page_title="Secure RAG Threat Intel", page_icon="🛡️", layout="wide")

st.title("🛡️ Secure RAG Threat Intelligence")
st.caption("Zero-Trust AI with Prompt Injection Defense and RBAC")

if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set your OPENAI_API_KEY environment variable.")
    st.stop()

# Sidebar for RBAC
st.sidebar.header("👤 User Context")
user_role = st.sidebar.radio("Select Your Role:", ["junior", "admin"])

# Initialize DB (Cached so it doesn't rebuild every time)
@st.cache_resource
def get_db():
    return setup_database()

vectorstore = get_db()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about CVEs or threat intel..."):
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Guardrail: Prompt Injection Check
    if check_prompt_injection(prompt):
        st.error("🚨 **SECURITY ALERT:** Prompt Injection Detected. Request blocked.")
        st.session_state.messages.append({"role": "assistant", "content": "Blocked by security guardrail."})
        st.stop()

    # 3. RAG Retrieval (with RBAC)
    with st.spinner("Searching authorized databases..."):
        context = secure_retrieval(prompt, user_role, vectorstore)

    # 4. LLM Generation
    with st.spinner("Generating response..."):
        raw_response = generate_secure_response(prompt, context)

    # 5. Guardrail: Output PII Redaction
    safe_response = redact_pii(raw_response)

    # 6. Display response
    with st.chat_message("assistant"):
        st.markdown(safe_response)
        
    st.session_state.messages.append({"role": "assistant", "content": safe_response})
