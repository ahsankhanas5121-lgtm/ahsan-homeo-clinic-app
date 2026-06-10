# Ahsan Homeo Clinic Management App

## 🏥 Overview

A comprehensive, production-ready clinic management system for **Ahsan Homeo Clinic & Store**, Karachi, Pakistan.

### Key Features
- 👥 **Patient Management** - Complete patient records with medical history
- 📅 **Appointment Scheduling** - Clinic visits and online consultations
- 💊 **Homeopathic Case Taking** - Detailed symptom documentation
- 📝 **Prescription Management** - Digital prescriptions with remedies
- 🔧 **Medicine Inventory** - Stock tracking and low-stock alerts
- 💰 **Billing & Invoicing** - Consultation and medicine charges
- 🌐 **Online Consultations** - Remote consultations (PKR 500)
- 📊 **Analytics & Reports** - Revenue, patient growth, statistics
- 🔐 **Role-Based Access Control** - Admin, Doctor, Receptionist

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Flutter (Android, iOS, Windows, Web) |
| **Backend** | FastAPI (Python 3.9+) |
| **Database** | PostgreSQL 13+ |
| **Authentication** | JWT Tokens |
| **Authorization** | Role-Based Access Control (RBAC) |
| **API Documentation** | OpenAPI/Swagger |
| **Containerization** | Docker & Docker Compose |

### Quick Links
- [Setup Guide](./docs/SETUP.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)
- [API Endpoints](./docs/API_ENDPOINTS.md)
- [ER Diagram](./docs/ER_DIAGRAM.md)

### Quick Start

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
flutter pub get
flutter run
```

#### Using Docker
```bash
docker-compose up -d
```

### Project Structure
```
ahsan-homeo-clinic-app/
├── backend/              # FastAPI Application
├── frontend/             # Flutter Application
├── docs/                 # Documentation
├── docker-compose.yml    # Docker configuration
└── README.md
```

### Clinic Information
- **Name:** Ahsan Homeo Clinic & Store
- **Location:** Karachi, Pakistan
- **Online Consultation Fee:** PKR 500

### License
Private Repository - Ahsan Homeo Clinic & Store
