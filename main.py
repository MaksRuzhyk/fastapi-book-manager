from fastapi import FastAPI, HTTPException
from app.books import router as books_router

app = FastAPI(title="Book Manager System", docs_url="/docs", redoc_url="/redoc")

@app.get("/status")
def status():
    return {'ok': True}


app.include_router(books_router)


