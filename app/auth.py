from pydantic import BaseModel, EmailStr, Field, field_validator

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


def get_user_by_email(cur, email: str):
    cur.execute("SELECT id, email, password_hash FROM users WHERE LOWER(email)=LOWER(%s)", (email,))
    return cur.fetchone()

def get_user_by_id(cur, uid: int):
    cur.execute("SELECT id, email FROM users WHERE id=%s", (uid,))
    return cur.fetchone()

