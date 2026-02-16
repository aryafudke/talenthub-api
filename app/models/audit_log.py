# app/models/audit_log.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who did it?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # What action?
    action = Column(String(50), nullable=False, index=True)
    # Examples: CREATE_EMPLOYEE, UPDATE_EMPLOYEE, DELETE_EMPLOYEE, etc.
    
    # On what entity?
    entity_type = Column(String(50), nullable=False, index=True)
    # Examples: employee, department, user
    
    entity_id = Column(Integer, nullable=True)
    # The ID of the affected record (nullable for bulk operations)
    
    # Additional details (JSON for flexibility)
    details = Column(JSON, nullable=True)
    # Store old values, new values, changed fields, etc.
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)
    
    # When?
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship to get user info
    user = relationship("User", backref="audit_logs")