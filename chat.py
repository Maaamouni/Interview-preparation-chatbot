from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# -----------------------
# CONFIG
# -----------------------
DB_PATH = "chroma_db"

# -----------------------
# 1. LOAD EMBEDDINGS (must match ingest.py)
# -----------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------
# 2. LOAD VECTOR DB
# -----------------------
vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# -----------------------
# 3. LOAD LLM (local via Ollama)
# -----------------------
llm = ChatOllama(model="llama3")  # or qwen2, mistral, etc.

# -----------------------
# 4. PROMPT TEMPLATE
# -----------------------
prompt = ChatPromptTemplate.from_template("""
You are an interview preparation assistant.

Use ONLY the context below to answer the question.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}

Answer:
""")

# -----------------------
# 5. CHAT LOOP
# -----------------------
def get_context(question):
    docs = retriever.invoke(question)

    context = ""
    sources = []

    for doc in docs:
        context += doc.page_content + "\n\n"

        sources.append({
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", "unknown"),
            "content_preview": doc.page_content[:80]
        })

    return context, sources

def chat():
    print("💬 RAG Chatbot ready! Type 'exit' to quit.\n")

    while True:
        question = input("You: ")

        if question.lower() == "exit":
            break

        context, sources = get_context(question)

        final_prompt = prompt.invoke({
            "context": context,
            "question": question
        })

        response = llm.invoke(final_prompt)

        print("\nBot:", response.content, "\n")

        print("\n Sources:")
        for s in sources:
            print(f" - {s['source']} (Page {s['page']}): {s['content_preview']}...")


if __name__ == "__main__":
    chat()