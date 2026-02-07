from pydantic import BaseModel, EmailStr
from typing import Optional 
from datetime import datetime 
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    
class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True