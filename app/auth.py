from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, user_id: str, password: str, sector: str) -> bool:
    user = db.query(User).filter(User.id == user_id, User.sector == sector).first()
    if not user:
        return False
    return verify_password(password, user.password_hash)

def get_current_user(request: Request):
    user_id = request.cookies.get("user_id")
    sector = request.cookies.get("sector")
    if not user_id or not sector:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user_id, sector