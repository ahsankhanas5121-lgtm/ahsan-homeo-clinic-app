# Database Schema - Ahsan Homeo Clinic Management App

## Tables Overview

### 1. Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL,  -- admin, doctor, receptionist
  is_active BOOLEAN DEFAULT TRUE,
  phone VARCHAR(20),
  department VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### 2. Patients Table
```sql
CREATE TABLE patients (
  id SERIAL PRIMARY KEY,
  patient_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., PAT-001
  full_name VARCHAR(100) NOT NULL,
  age INTEGER,
  gender VARCHAR(10),  -- Male, Female, Other
  phone VARCHAR(20),
  whatsapp_number VARCHAR(20),
  email VARCHAR(100),
  address TEXT,
  occupation VARCHAR(100),
  marital_status VARCHAR(20),  -- Single, Married, Divorced, Widowed
  height DECIMAL(5,2),  -- in cm
  weight DECIMAL(5,2),  -- in kg
  blood_group VARCHAR(5),
  
  -- Medical Information
  main_complaint TEXT,
  history_of_present_illness TEXT,
  past_history TEXT,
  family_history TEXT,
  allergies TEXT,
  current_medicines TEXT,
  
  created_by_user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### 3. Appointments Table
```sql
CREATE TABLE appointments (
  id SERIAL PRIMARY KEY,
  appointment_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., APT-001
  patient_id INTEGER NOT NULL REFERENCES patients(id),
  doctor_id INTEGER NOT NULL REFERENCES users(id),
  appointment_date DATE NOT NULL,
  appointment_time TIME NOT NULL,
  type VARCHAR(20) NOT NULL,  -- clinic_visit, online_consultation
  status VARCHAR(20) DEFAULT 'scheduled',  -- scheduled, completed, cancelled, follow_up
  notes TEXT,
  reminder_sent BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### 4. Consultations Table
```sql
CREATE TABLE consultations (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(20) UNIQUE NOT NULL,
  patient_id INTEGER NOT NULL REFERENCES patients(id),
  doctor_id INTEGER NOT NULL REFERENCES users(id),
  appointment_id INTEGER REFERENCES appointments(id),
  
  -- Homeopathic Case Taking
  mental_symptoms TEXT,
  physical_generals TEXT,
  thermals TEXT,
  food_desires TEXT,
  food_aversions TEXT,
  sleep_pattern TEXT,
  dreams TEXT,
  perspiration TEXT,
  female_complaints TEXT,
  male_complaints TEXT,
  particular_symptoms TEXT,
  
  consultation_notes TEXT,
  consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Prescriptions Table
```sql
CREATE TABLE prescriptions (
  id SERIAL PRIMARY KEY,
  prescription_id VARCHAR(20) UNIQUE NOT NULL,
  patient_id INTEGER NOT NULL REFERENCES patients(id),
  doctor_id INTEGER NOT NULL REFERENCES users(id),
  consultation_id INTEGER REFERENCES consultations(id),
  
  prescription_date DATE NOT NULL,
  notes TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Prescription Items Table
```sql
CREATE TABLE prescription_items (
  id SERIAL PRIMARY KEY,
  prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
  medicine_id INTEGER NOT NULL REFERENCES medicines(id),
  
  remedy_name VARCHAR(100),
  potency VARCHAR(20),  -- e.g., 30C, 200C
  dose VARCHAR(50),
  frequency VARCHAR(50),  -- e.g., 3 times daily
  duration VARCHAR(50),  -- e.g., 7 days
  instructions TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Medicines Table
```sql
CREATE TABLE medicines (
  id SERIAL PRIMARY KEY,
  medicine_code VARCHAR(20) UNIQUE NOT NULL,
  remedy_name VARCHAR(100) NOT NULL,
  source VARCHAR(100),
  potency VARCHAR(20),
  batch_number VARCHAR(50),
  quantity INTEGER NOT NULL DEFAULT 0,
  supplier_id INTEGER REFERENCES suppliers(id),
  purchase_price DECIMAL(10,2),
  sale_price DECIMAL(10,2),
  expiry_date DATE,
  
  -- Materia Medica Information
  keynotes TEXT,
  mind_symptoms TEXT,
  general_symptoms TEXT,
  particular_symptoms TEXT,
  relationships TEXT,
  modalities TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### 8. Suppliers Table
```sql
CREATE TABLE suppliers (
  id SERIAL PRIMARY KEY,
  supplier_name VARCHAR(100) NOT NULL,
  contact_person VARCHAR(100),
  phone VARCHAR(20),
  email VARCHAR(100),
  address TEXT,
  city VARCHAR(50),
  country VARCHAR(50),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9. Billing Invoices Table
```sql
CREATE TABLE billing_invoices (
  id SERIAL PRIMARY KEY,
  invoice_number VARCHAR(20) UNIQUE NOT NULL,
  patient_id INTEGER NOT NULL REFERENCES patients(id),
  appointment_id INTEGER REFERENCES appointments(id),
  
  consultation_fee DECIMAL(10,2) DEFAULT 0,
  medicine_charges DECIMAL(10,2) DEFAULT 0,
  other_charges DECIMAL(10,2) DEFAULT 0,
  total_amount DECIMAL(10,2) NOT NULL,
  
  payment_method VARCHAR(20),  -- cash, card, bank_transfer
  payment_status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, partial
  paid_amount DECIMAL(10,2) DEFAULT 0,
  remaining_amount DECIMAL(10,2),
  
  invoice_date DATE NOT NULL,
  due_date DATE,
  
  created_by_user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 10. Audit Logs Table
```sql
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(50),  -- create, update, delete, login
  table_name VARCHAR(100),
  record_id INTEGER,
  old_values JSONB,
  new_values JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Relationships

```
users (1) ──────────────────► (many) patients (created_by_user_id)
users (1) ──────────────────► (many) appointments (doctor_id)
users (1) ──────────────────► (many) consultations (doctor_id)
users (1) ──────────────────► (many) prescriptions (doctor_id)
users (1) ──────────────────► (many) billing_invoices (created_by_user_id)

patients (1) ─────────────► (many) appointments
patients (1) ─────────────► (many) consultations
patients (1) ─────────────► (many) prescriptions
patients (1) ─────────────► (many) billing_invoices

appointments (1) ───────► (many) consultations
appointments (1) ───────► (many) billing_invoices

consultations (1) ──────► (many) prescriptions

prescriptions (1) ──────► (many) prescription_items
prescription_items (many) → (1) medicines

medicines (many) ──────► (1) suppliers

suppliers (1) ─────────► (many) medicines
```

## Indexes

```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_consultations_patient_id ON consultations(patient_id);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_billing_invoices_patient_id ON billing_invoices(patient_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```
