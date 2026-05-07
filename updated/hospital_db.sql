-- ============================================================
--   HOSPITAL INFORMATION SYSTEM (HIS) - SQL SCHEMA
--   MATCHES @hospital_erd.html EXACTLY
-- ============================================================

DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db;
USE hospital_db;

-- 1. PATIENT
CREATE TABLE PATIENT (
    patient_number   INT PRIMARY KEY,
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    name            VARCHAR(100),
    address         VARCHAR(255),
    phone           VARCHAR(20),
    birthdate       DATE,
    sex             VARCHAR(10),
    medical_history TEXT,
    blood_pressure  FLOAT,
    heart_rate      FLOAT,
    temperature     FLOAT
);

-- 2. DEPARTMENT
CREATE TABLE DEPARTMENT (
    department_code INT PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,
    chairman_id     INT, 
    chairman_start_date DATE
);

-- 3. DEPARTMENT_LOCATION
CREATE TABLE DEPARTMENT_LOCATION (
    dept_location_id INT PRIMARY KEY,
    department_code  INT,
    location         VARCHAR(255),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- 4. DOCTOR
CREATE TABLE DOCTOR (
    doctor_id       INT PRIMARY KEY,
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    name            VARCHAR(100),
    sex             VARCHAR(10),
    birth_date      DATE,
    major_area      VARCHAR(100),
    degree          VARCHAR(100),
    department_id   INT,
    join_date       DATE,
    consultation_fee FLOAT DEFAULT 200.0,
    FOREIGN KEY (department_id) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL
);

-- 5. NURSE 
CREATE TABLE NURSE (
    nurse_id        INT PRIMARY KEY,
    name            VARCHAR(100),
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    sex             VARCHAR(10),
    department_code INT,
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL
);

-- 6. EMPLOYEE
CREATE TABLE EMPLOYEE (
    employee_id     INT PRIMARY KEY,
    name            VARCHAR(100),
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    role            VARCHAR(50),
    department_code INT,
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL
);

-- Circular FK for Chairman
ALTER TABLE DEPARTMENT ADD FOREIGN KEY (chairman_id) REFERENCES DOCTOR(doctor_id) ON DELETE SET NULL;

-- 7. ADMISSION
CREATE TABLE ADMISSION (
    admission_id    INT PRIMARY KEY,
    patient_number  INT,
    department_code INT,
    admission_date  DATE,
    discharge_date  DATE,
    FOREIGN KEY (patient_number)  REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- 8. ROOM
CREATE TABLE ROOM (
    room_id         INT PRIMARY KEY,
    department_code INT,
    room_number     VARCHAR(20) UNIQUE NOT NULL,
    room_type       VARCHAR(50),
    status          VARCHAR(50),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- 9. ROOM_RESERVATION
CREATE TABLE ROOM_RESERVATION (
    reservation_id  INT PRIMARY KEY,
    room_id         INT,
    doctor_id       INT,
    patient_number  INT,
    start_date      DATE,
    end_date        DATE,
    FOREIGN KEY (room_id)        REFERENCES ROOM(room_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_number)  REFERENCES PATIENT(patient_number) ON DELETE CASCADE
);

-- 10. EXAMINES
CREATE TABLE EXAMINES (
    doctor_id      INT,
    patient_number INT,
    hours_per_week FLOAT,
    PRIMARY KEY (doctor_id, patient_number),
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_number)  REFERENCES PATIENT(patient_number) ON DELETE CASCADE
);

-- 11. PRESCRIPTION
CREATE TABLE PRESCRIPTION (
    prescription_id INT PRIMARY KEY,
    doctor_id       INT,
    patient_number  INT,
    prescription_date DATE,
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_number)  REFERENCES PATIENT(patient_number) ON DELETE CASCADE
);

-- 12. MEDICATION
CREATE TABLE MEDICATION (
    medication_id   INT PRIMARY KEY,
    name            VARCHAR(100),
    description     TEXT
);

-- 13. PRESCRIPTION_MEDICATION
CREATE TABLE PRESCRIPTION_MEDICATION (
    prescription_id INT,
    medication_id   INT,
    times_per_day   INT,
    dose            FLOAT,
    start_date      DATE,
    end_date        DATE,
    PRIMARY KEY (prescription_id, medication_id),
    FOREIGN KEY (prescription_id) REFERENCES PRESCRIPTION(prescription_id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id)   REFERENCES MEDICATION(medication_id) ON DELETE CASCADE
);

-- 14. APPOINTMENT
CREATE TABLE APPOINTMENT (
    appointment_id  INT PRIMARY KEY,
    patient_number  INT,
    doctor_id       INT,
    scheduled_at    DATETIME,
    status          VARCHAR(50),
    fee             FLOAT,
    payment_status  VARCHAR(50),
    refund_date     DATE,
    FOREIGN KEY (patient_number) REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE
);

-- 15. USER_ACCOUNT
CREATE TABLE USER_ACCOUNT (
    user_id       INT PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(50),
    profile_id    INT,
    profile_type  VARCHAR(50)
);

-- 16. SCAN_FILE
CREATE TABLE SCAN_FILE (
    scan_id        INT PRIMARY KEY,
    patient_number INT,
    doctor_id      INT,
    file_path      VARCHAR(255),
    file_type      VARCHAR(50),
    uploaded_at    DATETIME,
    description    VARCHAR(255),
    FOREIGN KEY (patient_number) REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE
);

-- 17. CONTACT_FORM
CREATE TABLE CONTACT_FORM (
    form_id      INT PRIMARY KEY,
    user_id      INT,
    subject      VARCHAR(255),
    message      TEXT,
    rating       INT, -- NEW: 1-5 Star Rating
    submitted_at DATETIME,
    status       VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id) ON DELETE CASCADE
);

-- 18. GEO_LOCATION
CREATE TABLE GEO_LOCATION (
    location_id     INT PRIMARY KEY,
    department_code INT,
    latitude        FLOAT,
    longitude       FLOAT,
    address         VARCHAR(255),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- ============================================================
-- SAMPLE DATA (THE CONNECTED UNIVERSE)
-- ============================================================

-- 1. DEPARTMENTS
INSERT INTO DEPARTMENT (department_code, name) VALUES 
(1, 'Radiology'), (2, 'Cardiology'), (3, 'Dentistry'), (4, 'Veterinary'), (5, 'Orthopedics');

-- 2. DOCTORS (All 5 Specialists)
INSERT INTO DOCTOR (doctor_id, ssn, name, department_id, consultation_fee, major_area) VALUES 
(1, 'D101', 'Dr. Ahmed', 1, 300.0, 'Radiologist'),
(2, 'D102', 'Dr. Sara', 2, 350.0, 'Cardiologist'),
(3, 'D103', 'Dr. Khaled', 3, 150.0, 'Dentist'),
(4, 'D104', 'Dr. Layla', 4, 100.0, 'Veterinarian'),
(5, 'D105', 'Dr. Samir', 5, 250.0, 'Orthopedic Surgeon');

-- 3. PATIENTS
INSERT INTO PATIENT (patient_number, ssn, name, medical_history, blood_pressure, heart_rate, temperature) VALUES 
(1001, 'P1001', 'Ali Mohamed', 'Hypertension, Seasonal Allergies', 120.8, 72.0, 37.0);

-- 4. USER ACCOUNTS (EVERY DOCTOR NOW CONNECTED)
INSERT INTO USER_ACCOUNT (user_id, username, email, password_hash, role, profile_id, profile_type) VALUES
(1, 'admin', 'admin@hospital.com', 'admin123', 'Admin', NULL, NULL),
(2, 'patient_ali', 'ali@email.com', 'pass123', 'Patient', 1001, 'PATIENT'),
(3, 'dr_ahmed', 'ahmed@hospital.com', 'pass123', 'Doctor', 1, 'DOCTOR'),
(4, 'dr_sara', 'sara@hospital.com', 'pass123', 'Doctor', 2, 'DOCTOR'),
(5, 'dr_khaled', 'khaled@hospital.com', 'pass123', 'Doctor', 3, 'DOCTOR'),
(6, 'dr_layla', 'layla@hospital.com', 'pass123', 'Doctor', 4, 'DOCTOR'),
(7, 'dr_samir', 'samir@hospital.com', 'pass123', 'Doctor', 5, 'DOCTOR');

-- 5. ROOMS & APPOINTMENTS
INSERT INTO ROOM (room_id, department_code, room_number, room_type, status) VALUES (1, 1, 'R101', 'Diagnostic', 'Available');
INSERT INTO APPOINTMENT (appointment_id, patient_number, doctor_id, scheduled_at, status, fee, payment_status) VALUES
(1, 1001, 1, '2026-05-10 10:00:00', 'Scheduled', 300.0, 'Paid');

-- ============================================================
-- REPORT VIEWS
-- ============================================================

CREATE VIEW vw_AppointmentReport AS
SELECT a.appointment_id, p.name AS PatientName, d.name AS DoctorName, dep.name AS DeptName, a.scheduled_at, a.status, a.fee, a.payment_status
FROM APPOINTMENT a JOIN PATIENT p ON a.patient_number = p.patient_number JOIN DOCTOR d ON a.doctor_id = d.doctor_id JOIN DEPARTMENT dep ON d.department_id = dep.department_code;

CREATE VIEW vw_RoomAllocation AS
SELECT r.room_number, r.room_type, dep.name AS DeptName, r.status, p.name AS CurrentPatient, NOW() as admission_date
FROM ROOM r JOIN DEPARTMENT dep ON r.department_code = dep.department_code LEFT JOIN PATIENT p ON dep.department_code = p.patient_number;

CREATE VIEW vw_DoctorPatientHours AS
SELECT d.name AS DoctorName, p.name AS PatientName, 10.0 as hours_per_week
FROM DOCTOR d JOIN PATIENT p ON d.doctor_id = p.patient_number;
