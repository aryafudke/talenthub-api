# TalentHub API

> **Employee Management System with AI-Powered Natural Language Search**

A production-ready REST API built with FastAPI, featuring JWT authentication, role-based access control, and AI-powered smart search using Google Gemini.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Tests](https://img.shields.io/badge/Tests-16%20Passing-brightgreen.svg)

---

## Features

### Authentication & Authorization
- JWT-based authentication with secure token management
- Role-Based Access Control (RBAC) with three roles: Admin, HR, User
- Password hashing using bcrypt

### Employee Management
- Complete CRUD operations for employees
- Department management with foreign key relationships
- Pagination and filtering support

### AI-Powered Smart Search
- Natural language query processing using Google Gemini
- Convert queries like *"senior engineers in Mumbai earning above 15 LPA"* into database filters
- Intelligent fallback for unclear queries

### Reports & Analytics
- Summary statistics (total employees, departments, salary averages)
- Department-wise breakdown
- Hiring trends analysis
- SQL aggregations (COUNT, AVG, SUM, GROUP BY)

### Audit Logging
- Track all create, update, delete operations
- Records who did what and when
- Filterable audit logs for compliance

### Error Handling
- Custom exception classes
- Global exception handlers
- Consistent error response format

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.11+ |
| **Framework** | FastAPI |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt (passlib) |
| **AI/LLM** | Google Gemini API |
| **Validation** | Pydantic |
| **Testing** | pytest |
| **Containerization** | Docker & Docker Compose |

---

## Project Structure
```
talenthub-api/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Settings & environment
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── department.py
│   │   └── audit_log.py
│   ├── schemas/                # Pydantic schemas
│   ├── routers/                # API endpoints
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── departments.py
│   │   ├── smart_search.py
│   │   ├── reports.py
│   │   └── audit_logs.py
│   ├── services/               # Business logic
│   │   ├── llm_service.py      # Gemini integration
│   │   └── audit_service.py
│   ├── core/                   # Utilities
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   └── exception_handlers.py
│   └── database/
│       └── connection.py
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Google Gemini API Key

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/talenthub-api.git
cd talenthub-api

# Set your Gemini API key
export GEMINI_API_KEY=your_api_key_here

# Start with Docker
docker-compose up --build
```

Visit `http://localhost:8000/docs` for Swagger UI.

### Option 2: Local Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/talenthub-api.git
cd talenthub-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and API keys

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/auth/register` | Register new user | Public |
| POST | `/auth/login` | Login & get token | Public |
| GET | `/auth/me` | Get current user | Authenticated |

### Employees
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/employees` | List all employees | All Users |
| GET | `/employees/{id}` | Get single employee | All Users |
| POST | `/employees` | Create employee | Admin, HR |
| PUT | `/employees/{id}` | Update employee | Admin, HR |
| DELETE | `/employees/{id}` | Delete employee | Admin Only |
| POST | `/employees/smart-search` | AI-powered search | All Users |

### Departments
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/departments` | List departments | All Users |
| POST | `/departments` | Create department | Admin Only |
| PUT | `/departments/{id}` | Update department | Admin Only |
| DELETE | `/departments/{id}` | Delete department | Admin Only |

### Reports
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/reports/summary` | Overall statistics | All Users |
| GET | `/reports/department-stats` | Department breakdown | Admin, HR |
| GET | `/reports/salary-stats` | Salary analytics | Admin, HR |
| GET | `/reports/hiring-trends` | Hiring trends | All Users |

### Audit Logs
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/audit-logs` | List audit logs | Admin Only |
| GET | `/audit-logs/{id}` | Get single log | Admin Only |

---

##  Smart Search Examples

The AI-powered search converts natural language to database queries:
```bash
# Example 1: Find by role and location
POST /employees/smart-search
{
  "query": "senior engineers in Mumbai"
}

# Example 2: Filter by salary
POST /employees/smart-search
{
  "query": "employees earning above 20 LPA"
}

# Example 3: Complex query
POST /employees/smart-search
{
  "query": "active developers hired after 2023 in Bangalore"
}
```

---

## Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

**Current Status: 16 tests passing **

---

##  Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all resources |
| **HR** | Create/Update employees, View reports |
| **User** | Read-only access to employees |

---

##  Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/talenthub` |
| `SECRET_KEY` | JWT signing key | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `GEMINI_API_KEY` | Google Gemini API key | `your-gemini-key` |

