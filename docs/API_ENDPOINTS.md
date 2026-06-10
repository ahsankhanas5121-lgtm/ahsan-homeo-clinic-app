# API Endpoints - Ahsan Homeo Clinic Management App

## Base URL
`http://localhost:8000/api/v1`

## Authentication Endpoints

### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "doctor1",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "doctor1",
    "role": "doctor",
    "full_name": "Dr. Ahmed"
  }
}
```

### Refresh Token
```
POST /auth/refresh
Authorization: Bearer {refresh_token}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Logout
```
POST /auth/logout
Authorization: Bearer {access_token}

Response:
{
  "message": "Successfully logged out"
}
```

## Patient Endpoints

### Get All Patients
```
GET /patients
Authorization: Bearer {access_token}

Response:
{
  "items": [
    {
      "id": 1,
      "patient_id": "PAT-001",
      "full_name": "Ali Ahmed",
      "age": 35,
      "gender": "Male",
      "phone": "03001234567",
      "email": "ali@example.com"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### Create Patient
```
POST /patients
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Ali Ahmed",
  "age": 35,
  "gender": "Male",
  "phone": "03001234567",
  "email": "ali@example.com",
  "address": "Karachi, Pakistan",
  "blood_group": "O+"
}

Response:
{
  "id": 1,
  "patient_id": "PAT-001",
  "full_name": "Ali Ahmed",
  "created_at": "2024-01-01T10:00:00"
}
```

### Get Patient Details
```
GET /patients/{patient_id}
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "patient_id": "PAT-001",
  "full_name": "Ali Ahmed",
  "age": 35,
  "medical_history": [...],
  "appointments": [...]
}
```

### Update Patient
```
PUT /patients/{patient_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Ali Ahmed Khan",
  "age": 36
}
```

## Appointment Endpoints

### Get Appointments
```
GET /appointments
Authorization: Bearer {access_token}

Parameters:
  - date: (optional) Filter by date
  - doctor_id: (optional) Filter by doctor
  - status: (optional) scheduled, completed, cancelled

Response:
{
  "items": [
    {
      "id": 1,
      "appointment_id": "APT-001",
      "patient": {...},
      "doctor": {...},
      "date": "2024-01-15",
      "time": "10:00",
      "status": "scheduled",
      "type": "clinic_visit"
    }
  ]
}
```

### Create Appointment
```
POST /appointments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 2,
  "date": "2024-01-15",
  "time": "10:00",
  "type": "clinic_visit",
  "notes": "Follow-up consultation"
}

Response:
{
  "id": 1,
  "appointment_id": "APT-001",
  "status": "scheduled",
  "created_at": "2024-01-01T10:00:00"
}
```

### Update Appointment Status
```
PUT /appointments/{appointment_id}/status
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "completed"
}

Response:
{
  "id": 1,
  "status": "completed",
  "updated_at": "2024-01-15T10:30:00"
}
```

## More Endpoints
See full documentation at `/docs` (Swagger UI)
