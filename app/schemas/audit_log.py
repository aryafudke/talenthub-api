# app/schemas/audit_log.py

from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


# Response schema for single audit log
class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Response for list of audit logs
class AuditLogListResponse(BaseModel):
    total_count: int
    logs: list[AuditLogResponse]