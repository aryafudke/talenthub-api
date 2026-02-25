# tests/test_employees.py

import pytest
from datetime import date


class TestCreateEmployee:
    """Test employee creation"""
    
    def test_create_employee_as_admin(self, client, admin_token, test_department):
        """Admin can create employee"""
        response = client.post(
            "/employees/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "employee_id": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@company.com",
                "department_id": test_department.id,
                "designation": "Software Engineer",
                "salary": 1500000,
                "hire_date": "2024-01-15",
                "location": "Mumbai",
                "status": "active"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == "EMP001"
        assert data["first_name"] == "John"
    
    def test_create_employee_as_hr(self, client, hr_token, test_department):
        """HR can create employee"""
        response = client.post(
            "/employees/",
            headers={"Authorization": f"Bearer {hr_token}"},
            json={
                "employee_id": "EMP002",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@company.com",
                "department_id": test_department.id,
                "designation": "Designer",
                "salary": 1200000,
                "hire_date": "2024-02-01",
                "location": "Delhi",
                "status": "active"
            }
        )
        
        assert response.status_code == 201
    
    def test_create_employee_as_user_forbidden(self, client, user_token, test_department):
        """Regular user cannot create employee"""
        response = client.post(
            "/employees/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "employee_id": "EMP003",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@company.com",
                "department_id": test_department.id,
                "designation": "Tester",
                "salary": 1000000,
                "hire_date": "2024-03-01",
                "location": "Chennai",
                "status": "active"
            }
        )
        
        assert response.status_code == 403


class TestGetEmployees:
    """Test getting employees"""
    
    def test_get_employees_as_user(self, client, user_token):
        """Any logged-in user can view employees"""
        response = client.get(
            "/employees/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_employees_no_auth(self, client):
        """Cannot view employees without login"""
        response = client.get("/employees/")
        
        assert response.status_code == 401


class TestDeleteEmployee:
    """Test employee deletion"""
    
    def test_delete_employee_as_admin(self, client, admin_token, test_department):
        """Admin can delete employee"""
        # First create an employee
        create_response = client.post(
            "/employees/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "employee_id": "EMP999",
                "first_name": "Delete",
                "last_name": "Me",
                "email": "delete@company.com",
                "department_id": test_department.id,
                "designation": "Temp",
                "salary": 500000,
                "hire_date": "2024-01-01",
                "location": "Test",
                "status": "active"
            }
        )
        
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Now delete
        response = client.delete(
            f"/employees/{employee_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    def test_delete_employee_as_hr_forbidden(self, client, admin_token, hr_token, test_department):
        """HR cannot delete employee"""
        # First create an employee as admin
        create_response = client.post(
            "/employees/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "employee_id": "EMP888",
                "first_name": "Cannot",
                "last_name": "Delete",
                "email": "nodelete@company.com",
                "department_id": test_department.id,
                "designation": "Protected",
                "salary": 500000,
                "hire_date": "2024-01-01",
                "location": "Test",
                "status": "active"
            }
        )
        
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to delete as HR (should fail)
        response = client.delete(
            f"/employees/{employee_id}",
            headers={"Authorization": f"Bearer {hr_token}"}
        )
        
        assert response.status_code == 403