from rag_core import load_and_chunk, create_vectorstore, ask

pdf_path = "test.pdf"  # put any PDF in your project folder

chunks = load_and_chunk(pdf_path)
vs = create_vectorstore(chunks)

result = ask(vs, "What is this document about?")
print("\n=== ANSWER ===")
print(result["answer"])
print("\n=== SOURCES ===")
for s in result["sources"]:
    print(f"  Page {s['page']}: {s['snippet']}...")