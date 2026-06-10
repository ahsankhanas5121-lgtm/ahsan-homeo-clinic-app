# System Architecture - Ahsan Homeo Clinic Management App

## Overview

Clean Architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│   Presentation Layer (Flutter)                  │
│   Screens, Widgets, Theme, Navigation           │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│   API Client Layer                              │
│   HTTP Requests, Interceptors                   │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│   REST API (FastAPI)                            │
│   Routes, Endpoints, Validation                 │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│   Service Layer                                 │
│   Business Logic, Validations                   │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│   Data Access Layer (ORM)                       │
│   SQLAlchemy Models                             │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│   Database Layer (PostgreSQL)                   │
│   Persistent Data Storage                       │
└─────────────────────────────────────────────────┘
```

## Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration
│   ├── core/
│   │   ├── security.py          # JWT, Password hashing
│   │   ├── permissions.py       # RBAC
│   │   └── constants.py         # Constants
│   ├── database/
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   └── schemas.py           # Pydantic schemas
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Router aggregator
│   │       └── endpoints/       # API endpoints
│   │           ├── auth.py
│   │           ├── patients.py
│   │           └── ...
│   ├── services/                 # Business logic
│   ├── middleware/               # HTTP middleware
│   └── utils/                    # Utilities
├── migrations/                   # Alembic migrations
├── tests/                        # Unit & integration tests
├── requirements.txt
└── Dockerfile
```

## Frontend Structure

```
frontend/
├── lib/
│   ├── main.dart                # Entry point
│   ├── config/                  # Configuration
│   ├── models/                  # Data models
│   ├── screens/                 # UI screens
│   ├── widgets/                 # Reusable widgets
│   ├── services/                # API services
│   ├── providers/               # State management
│   ├── theme/                   # App theme
│   └── utils/                   # Utilities
├── test/                        # Tests
├── pubspec.yaml
└── Dockerfile
```

## Security Architecture

### Authentication
- JWT tokens with 30-minute expiry
- Refresh tokens with 7-day expiry
- bcrypt password hashing

### Authorization
- Role-Based Access Control (RBAC)
- Roles: Admin, Doctor, Receptionist
- Permission checks at endpoint level

### Protection Layers
1. API Layer: JWT validation
2. Service Layer: Role/permission checks
3. Database Layer: SQL injection prevention
4. Transport: HTTPS in production
