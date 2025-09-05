from fastapi import FastAPI, HTTPException
from routers.books import router as books_router
from routers.auth import router as auth_router
from routers.imports import router as imports_router
from routers.export import router as export_router

app = FastAPI(title="Book Manager System", docs_url="/docs", redoc_url="/redoc")

@app.get("/status")
def status():
    return {'ok': True}

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(imports_router)
app.include_router(export_router)


