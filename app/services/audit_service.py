# app/services/audit_service.py

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.models.audit_log import AuditLog
from app.models.user import User


# Action constants
class AuditAction:
    # Employee actions
    CREATE_EMPLOYEE = "CREATE_EMPLOYEE"
    UPDATE_EMPLOYEE = "UPDATE_EMPLOYEE"
    DELETE_EMPLOYEE = "DELETE_EMPLOYEE"
    
    # Department actions
    CREATE_DEPARTMENT = "CREATE_DEPARTMENT"
    UPDATE_DEPARTMENT = "UPDATE_DEPARTMENT"
    DELETE_DEPARTMENT = "DELETE_DEPARTMENT"
    
    # User actions
    USER_LOGIN = "USER_LOGIN"
    USER_REGISTER = "USER_REGISTER"
    
    # Search actions
    SMART_SEARCH = "SMART_SEARCH"


def create_audit_log(
    db: Session,
    user: User,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Create an audit log entry.
    
    Usage:
        create_audit_log(
            db=db,
            user=current_user,
            action=AuditAction.CREATE_EMPLOYEE,
            entity_type="employee",
            entity_id=new_employee.id,
            details={"employee_id": "EMP001", "name": "John Doe"}
        )
    """
    
    audit_log = AuditLog(
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log