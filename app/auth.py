from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.db import conn, get_dict_cursor
from app.security import hash_pwd, verify_pwd, make_token, decode_token

router = APIRouter(prefix="/auth", tags=['auth'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль повинен бути не менше 8 символів.")
        if not any(ch.isupper() for ch in v):
            raise ValueError("Пароль повинен містити хоча б одну велику літеру.")
        if not any(ch.islower() for ch in v):
            raise ValueError("Пароль повинен містити хоча б одну маленьку літеру.")
        if not any(ch.isdigit() for ch in v):
            raise ValueError("Пароль повинен містити хоча б одне число.")
        special = "!@#$%^&*(),.?\":{}|<>"
        if not any(ch in special for ch in v):
            raise ValueError("Пароль повинен містити хоча б один спец.символ.")
        return v


def _get_user_by_email(cur, email: str):
    cur.execute("SELECT id, email, password_hash FROM users WHERE LOWER(email)=LOWER(%s)", (email,))
    return cur.fetchone()

def _get_user_by_id(cur, uid: int):
    cur.execute("SELECT id, email FROM users WHERE id=%s", (uid,))
    return cur.fetchone()

@router.post("/signup", status_code=201)
def signup(payload: SignupIn):
    with conn() as c, get_dict_cursor(c) as cur:
        if _get_user_by_email(cur, str(payload.email)):
            raise HTTPException(status_code=409, detail="Користувач вже існує")

        cur.execute(
            "INSERT INTO users(email, password_hash) VALUES (%s,%s)",
            (payload.email, hash_pwd(payload.password)),
        )
        return {"ok": True}

@router.post("/token", response_model=Token)
def login_for_access_token(form: OAuth2PasswordRequestForm = Depends()):
    with conn() as c, get_dict_cursor(c) as cur:
        user = _get_user_by_email(cur, form.username)
        if not user or not verify_pwd(form.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Неправильний логін або пароль")
        token = make_token(str(user['id']))
        return Token(access_token=token)

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        data = decode_token(token)
        return int(data["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Недійсний токен")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        uid = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    with conn() as c, get_dict_cursor(c) as cur:
        user = _get_user_by_id(cur, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user