"""API v1 Router - Aggregates all endpoints"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, patients, appointments

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(appointments.router)

# Health check endpoint is in main.py
