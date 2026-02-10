# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}


from fastapi import FastAPI
from app.routers import auth, departments

app = FastAPI(
    title="TalentHub API",
    description = "Employee Management System + AI-Powered Search",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(departments.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}