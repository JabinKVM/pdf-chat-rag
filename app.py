import streamlit as st
import os
import tempfile
from rag_core import load_and_chunk, create_vectorstore, ask

st.set_page_config(
    page_title="DocMind — Chat with any PDF",
    page_icon="📄",
    layout="centered"
)

# ── custom css ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 600;
    }
    .main-header p {
        color: #888;
        font-size: 0.95rem;
    }
    .stat-row {
        display: flex;
        gap: 1rem;
        margin: 0.5rem 0 1rem 0;
    }
    .stat-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #555;
        border: 1px solid #eee;
    }
    .source-box {
        background: #f8f9fa;
        border-left: 3px solid #4CAF50;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── header ────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📄 PDF Chat Assistant</h1>
    <p>Upload any PDF and have a conversation with it — powered by RAG</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("**How it works**")
    st.caption("1. Upload a PDF")
    st.caption("2. Ask any question")
    st.caption("3. Get answers with sources")
    st.divider()
    st.caption("Built with LangChain · ChromaDB · Groq · Streamlit")

# ── session state ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "pdf_stats" not in st.session_state:
    st.session_state.pdf_stats = None

# ── process uploaded PDF ──────────────────────────────────────────
if uploaded_file and uploaded_file.name != st.session_state.current_file:
    progress = st.progress(0, text="📖 Saving your PDF...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    progress.progress(25, text="✂️ Splitting into chunks...")
    chunks = load_and_chunk(tmp_path)

    progress.progress(50, text="🧠 Creating embeddings... (this takes a moment)")
    st.session_state.vectorstore = create_vectorstore(chunks)

    progress.progress(85, text="💾 Storing in vector database...")
    st.session_state.current_file = uploaded_file.name
    st.session_state.messages = []
    st.session_state.pdf_stats = {
        "chunks": len(chunks),
        "name": uploaded_file.name,
        "size": f"{uploaded_file.size // 1024} KB"
    }
    os.unlink(tmp_path)
    progress.progress(100, text="✅ Done!")
    st.success("✅ Ready! Ask anything below.")

# ── PDF stats bar ─────────────────────────────────────────────────
if st.session_state.pdf_stats:
    stats = st.session_state.pdf_stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 File", stats["name"][:20] + "..." if len(stats["name"]) > 20 else stats["name"])
    with col2:
        st.metric("🧩 Chunks", stats["chunks"])
    with col3:
        st.metric("💾 Size", stats["size"])
    st.divider()

# ── welcome message ───────────────────────────────────────────────
if not st.session_state.messages and st.session_state.vectorstore is None:
    st.info("👈 Upload a PDF from the sidebar to get started.")

if not st.session_state.messages and st.session_state.vectorstore is not None:
    st.info("💬 Your PDF is ready! Ask your first question below.")

# ── chat history ──────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander("📚 View sources"):
                for i, source in enumerate(msg["sources"], 1):
                    st.markdown(f"""<div class="source-box">
                        <strong>Source {i} — Page {source['page']}</strong><br>
                        {source['snippet']}...
                    </div>""", unsafe_allow_html=True)

# ── chat input ────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about your PDF..."):
    if st.session_state.vectorstore is None:
        st.warning("⚠️ Please upload a PDF first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                result = ask(
                    st.session_state.vectorstore,
                    prompt,
                    st.session_state.messages
                )
                answer = result["answer"]
                st.markdown(answer)

                with st.expander("📚 View sources"):
                    for i, source in enumerate(result["sources"], 1):
                        st.markdown(f"""<div class="source-box">
                            <strong>Source {i} — Page {source['page']}</strong><br>
                            {source['snippet']}...
                        </div>""", unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": result["sources"]
        })