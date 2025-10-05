from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Foursquare AI Bot API", description="API for querying POI data using DuckDB and LangChain.")

@app.get("/")
def read_root():
    return {"message": "Foursquare AI Bot API is running!"}

# Example endpoint for health check
@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})

# You can add more endpoints here for your bot logic

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
