from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from pydantic import BaseModel

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

DB_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

llm = ChatOllama(model="llama3")

prompt = ChatPromptTemplate.from_template("""
You are an interview preparation assistant.

Use only the provided context.

Context:
{context}

Question:
{question}

Answer:
""")


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/chat")
async def chat(req: ChatRequest):

    docs = retriever.invoke(req.message)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    sources = [
        {
            "file": doc.metadata.get("source"),
            "page": doc.metadata.get("page")
        }
        for doc in docs
    ]

    final_prompt = prompt.invoke(
        {
            "context": context,
            "question": req.message
        }
    )

    response = llm.invoke(final_prompt)

    return {
        "answer": response.content,
        "sources": sources
    }