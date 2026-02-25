# tests/test_auth.py

import pytest


class TestRegister:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        # assert data["full_name"] == "New User"
        assert "password" not in data  # Password should not be returned!

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@test.com",  # Already exists!
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "full_name": "Bad Email User"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@test.com",
                "password": "user123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nobody@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestGetMe:
    """Test get current user"""
    
    def test_get_me_success(self, client, test_user, user_token):
        """Test getting current user profile"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@test.com"
    
    def test_get_me_no_token(self, client):
        """Test getting profile without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401  # no token
    
    def test_get_me_invalid_token(self, client):
        """Test getting profile with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        
        assert response.status_code == 401