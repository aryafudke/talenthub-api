from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from app.database.connection import get_db 
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    #checks if email already exists
    existing_user = db.query(User).filter(User.email== user_data.email).first()
    if existing_user :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Email already registered"
        )
        
     #creating new user
    new_user = User(
         email = user_data.email,
         password_hash = hash_password(user_data.password),
         full_name = user_data.full_name
    )   
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user