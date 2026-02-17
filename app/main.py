# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}


from fastapi import FastAPI
from app.routers import auth, departments
from app.routers.employees import router as employees_router
from app.routers.smart_search import router as smart_search_router
from app.routers.reports import router as reports_router
from app.routers.audit_logs import router as audit_logs_router
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import TalentHubException
from app.core.exception_handlers import (
    talenthub_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

app = FastAPI(
    title="TalentHub API",
    description = "Employee Management System + AI-Powered Search",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees_router)
app.include_router(smart_search_router)
app.include_router(reports_router)
app.include_router(audit_logs_router)
app.add_exception_handler(TalentHubException, talenthub_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/health")
def health_check():
    return {"status": "healthy"}