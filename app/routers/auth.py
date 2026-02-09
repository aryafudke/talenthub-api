from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from app.database.connection import get_db 
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.core.security import hash_password
from app.core.dependencies import get_current_user


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

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    #find user by email 
    user = db.query(User).filter(User.email == login_data.email).first()
    
    #check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
        
    #check if password is correct 
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    
    #check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "User account is disabled"
        )
        
     #create token with user info
    token_data ={
         "sub": str(user.id),
         "email": user.email,
         "role":  user.role.value
     }  
    
    access_token = create_access_token(data=token_data)
    
    return {"access_token":access_token, "token_type": "bearer"} 


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user 
        
        
        