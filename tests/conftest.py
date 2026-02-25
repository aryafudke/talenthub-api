# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.employee import Employee
from app.core.security import hash_password


# Create test database (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Create test client
@pytest.fixture(scope="function")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


# Create test database session
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    yield session
    session.close()
    
    Base.metadata.drop_all(bind=engine)


# Create test users
@pytest.fixture
def test_admin(db_session):
    """Create admin user for testing"""
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        full_name="Test Admin",
        role=UserRole.admin,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_hr(db_session):
    """Create HR user for testing"""
    hr = User(
        email="hr@test.com",
        password_hash=hash_password("hr123"),
        full_name="Test HR",
        role=UserRole.hr,
        is_active=True
    )
    db_session.add(hr)
    db_session.commit()
    db_session.refresh(hr)
    return hr


@pytest.fixture
def test_user(db_session):
    """Create regular user for testing"""
    user = User(
        email="user@test.com",
        password_hash=hash_password("user123"),
        full_name="Test User",
        role=UserRole.user,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_department(db_session):
    """Create test department"""
    department = Department(
        name="Engineering",
        description="Engineering Department"
    )
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)
    return department


# Helper function to get auth token
def get_auth_token(client, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin):
    return get_auth_token(client, "admin@test.com", "admin123")


@pytest.fixture
def hr_token(client, test_hr):
    return get_auth_token(client, "hr@test.com", "hr123")


@pytest.fixture
def user_token(client, test_user):
    return get_auth_token(client, "user@test.com", "user123")