from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from routers.auth import get_current_user_id
from app.imports import parse_upload, import_books_items

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/import")
async def import_books(file: UploadFile = File(..., description="JSON або CSV з книгами"),
                       user_id: int = Depends(get_current_user_id)):
    raw = await file.read()
    try:
        items = parse_upload(file.filename or "", file.content_type, raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    created, skipped, errors = import_books_items(items, user_id)
    return {"ok": True, "created": created, "skipped": skipped, "errors": errors[:200]}