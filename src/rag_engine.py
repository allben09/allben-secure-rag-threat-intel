"""
src/rag_engine.py
Secure RAG pipeline with ChromaDB and RBAC.
"""
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

# Mock Threat Intel Documents
DOCUMENTS = [
    {"text": "CVE-2024-1234: Critical RCE in Apache Struts. Patch immediately.", "role": "public"},
    {"text": "CVE-2024-5678: Zero-day in FNB internal banking app. Source IP: 192.168.1.50", "role": "top_secret"},
]

def setup_database():
    """Initializes ChromaDB with role-based metadata."""
    embeddings = OpenAIEmbeddings()
    
    texts = [doc["text"] for doc in DOCUMENTS]
    metadatas = [{"role": doc["role"]} for doc in DOCUMENTS]
    
    # Create the vector store
    vectorstore = Chroma.from_texts(
        texts=texts, 
        embedding=embeddings, 
        metadatas=metadatas,
        collection_name="threat_intel"
    )
    return vectorstore

def secure_retrieval(query: str, user_role: str, vectorstore):
    """Retrieves documents, but ONLY if the user has the right role."""
    
    # RBAC Filter: If user is 'junior', only search 'public' docs
    search_filter = {"role": "public"} if user_role == "junior" else None
    
    # Perform similarity search with filter
    results = vectorstore.similarity_search(
        query, 
        k=2, 
        filter=search_filter
    )
    
    return "\n".join([res.page_content for res in results])

def generate_secure_response(query: str, context: str):
    """Generates an LLM response using the secure context."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful SOC assistant. Answer the question based ONLY on the context below.\n"
        "Context: {context}\n"
        "Question: {query}"
    )
    
    chain = prompt | llm
    return chain.invoke({"context": context, "query": query}).content
