# app/routers/audit_logs.py

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse
from app.core.dependencies import get_admin_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=AuditLogListResponse)
def get_audit_logs(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Records to return"),
    action: Optional[str] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    days: Optional[int] = Query(None, description="Filter by last N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Only Admin can view!
):
    """
    Get audit logs with filters. Only accessible by Admin.
    """
    
    query = db.query(AuditLog)
    
    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(AuditLog.timestamp >= cutoff_date)
    
    # Get total count
    total_count = query.count()
    
    # Get logs with pagination, newest first
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Add user email to response
    log_responses = []
    for log in logs:
        log_response = AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=log.user.email if log.user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            timestamp=log.timestamp
        )
        log_responses.append(log_response)
    
    return AuditLogListResponse(
        total_count=total_count,
        logs=log_responses
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get single audit log by ID. Only accessible by Admin.
    """
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_email=log.user.email if log.user else None,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        details=log.details,
        ip_address=log.ip_address,
        timestamp=log.timestamp
    )