from sqlalchemy import Column, Integer, String,Boolean, DateTime,Enum
from sqlalchemy.sql import func 
import enum 
from app.database.connection import Base

class UserRole(enum.Enum):
    admin = "admin"
    hr = "hr"
    user = "user"
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default = UserRole.user)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
# if __name__ == "__main__":
#     from app.database.connection import engine
#     Base.metadata.create_all(bind=engine)
#     print("Table created!")
    