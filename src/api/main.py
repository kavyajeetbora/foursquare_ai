from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.langchain.pipeline import initiate_chat_bot
from langchain_core.prompts import ChatPromptTemplate
import os

app = FastAPI(title="Foursquare AI Bot API", description="API for querying POI data using DuckDB and LangChain.")
BOT = initiate_chat_bot()

@app.get("/")
def read_root():
    return {"message": "Foursquare AI Bot API is running!"}

# Example endpoint for health check
@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    result = BOT.process_question(request.question)
    return {
        "query": result["state"].query,
        "result": result["state"].result,
        "answer": result["state"].answer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
