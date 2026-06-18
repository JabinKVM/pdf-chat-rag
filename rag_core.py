import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

load_dotenv()

def load_and_chunk(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} pages")
    return chunks

def create_vectorstore(chunks, persist_dir="chroma_db"):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # wipe old data so no duplicates ever build up
    import shutil
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB")
    return vectorstore

def retrieve(vectorstore, query: str, k: int = 6) -> list:
    results = vectorstore.similarity_search(query, k=k)
    
    # remove duplicate chunks by content
    seen = set()
    unique = []
    for doc in results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique.append(doc)
    
    return unique

def generate_answer(query: str, chunks: list, chat_history: list = []) -> str:
    context = "\n\n---\n\n".join([c.page_content for c in chunks])

    # build history text
    history_text = ""
    if chat_history:
        history_text = "Previous conversation:\n"
        for msg in chat_history[-4:]:  # last 4 messages only
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
        history_text += "\n"

    prompt = f"""You are a helpful assistant. Answer the user's question 
using ONLY the context provided below. If the answer is not in the context,
say "I couldn't find that in the document."

{history_text}
Context:
{context}

Current question: {query}

Answer:"""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content


def ask(vectorstore, query: str, chat_history: list = []) -> dict:
    chunks = retrieve(vectorstore, query)
    answer = generate_answer(query, chunks, chat_history)
    sources = [
        {"page": c.metadata.get("page", "?"), "snippet": c.page_content[:150]}
        for c in chunks
    ]
    return {"answer": answer, "sources": sources}