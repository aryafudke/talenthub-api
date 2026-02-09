import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta]= None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta # custom expiry
    else:
        expire = datetime.utcnow() + timedelta(minutes=30) # default 30 mins
        
    to_encode.update({"exp":expire}) # add expiry to token data
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm = settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload # return user data if valid 
    except JWTError:
        return None # return None if invalid/expired