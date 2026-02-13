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

@app.get("/health")
def health_check():
    return {"status": "healthy"}