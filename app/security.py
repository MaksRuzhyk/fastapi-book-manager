import os
import time
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALG = os.getenv("JWT_ALG")
ACCESS_TTL = int(os.getenv("ACCESS_TTL"))

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pwd(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_pwd(password: str, password_hash: str) -> bool:
    return pwd_ctx.verify(password, password_hash)

def make_token(sub: str, extra: dict | None = None, ttl: int = ACCESS_TTL) -> str:
    now = time.time()
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + ttl
    }

    if extra:
        payload.update(extra)

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
