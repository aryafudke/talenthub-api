# app/schemas/error.py

from pydantic import BaseModel
from typing import Any, Optional, Dict


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail