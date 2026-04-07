from fastapi import FastAPI
from rag import load_rag
from model import Prompt, Response
from dotenv import load_dotenv
load_dotenv()
    
app = FastAPI()
chain = load_rag()
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/rag_chain")
async def rag_chain(prompt: Prompt):
    answer=""
    prompt_dump = prompt.model_dump()
    try:
        for chunk in chain.stream(prompt_dump):
            answer += chunk

    except Exception as e:
        answer = f"Error: {e}"

    return Response(answer).model_dump()