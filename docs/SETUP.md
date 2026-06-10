# Setup Guide - Ahsan Homeo Clinic Management App

## Prerequisites

### System Requirements
- **OS:** Linux, macOS, or Windows (WSL2 recommended)
- **Python:** 3.9 or higher
- **PostgreSQL:** 13 or higher
- **Flutter SDK:** Latest stable version
- **Git:** 2.30 or higher
- **Docker & Docker Compose:** Latest versions (optional but recommended)

## Backend Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/ahsankhanas5121-lgtm/ahsan-homeo-clinic-app.git
cd ahsan-homeo-clinic-app
```

### Step 2: Create Virtual Environment
```bash
cd backend
python3.9 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\\Scripts\\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ahsan_homeo_clinic

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

### Step 5: Create PostgreSQL Database
```bash
# Create database
sudo -u postgres psql
CREATE USER ahsan_clinic WITH PASSWORD 'secure_password';
CREATE DATABASE ahsan_homeo_clinic OWNER ahsan_clinic;
```

### Step 6: Run Migrations
```bash
alembic upgrade head
```

### Step 7: Start Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`

## Frontend Setup

### Step 1: Navigate to Frontend
```bash
cd ../frontend
```

### Step 2: Get Dependencies
```bash
flutter pub get
```

### Step 3: Run App
```bash
flutter run
```

## Docker Setup

```bash
# From project root
docker-compose up -d
```

Services available:
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Swagger Docs: `http://localhost:8000/docs`
