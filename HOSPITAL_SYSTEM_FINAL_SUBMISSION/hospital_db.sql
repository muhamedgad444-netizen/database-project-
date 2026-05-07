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
    temperature     FLOAT,
    blood_type      VARCHAR(5),
    CONSTRAINT chk_patient_sex CHECK (sex IN ('Male', 'Female', 'Other')),
    CONSTRAINT chk_vitals CHECK (blood_pressure > 0 AND heart_rate > 0 AND temperature > 0)
);

-- 2. DEPARTMENT
CREATE TABLE DEPARTMENT (
    department_code INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) UNIQUE NOT NULL,
    chairman_id     INT UNIQUE NULL, -- FIX: Nullable to prevent circular insertion deadlock
    chairman_start_date DATE
);

-- 3. DEPARTMENT_LOCATION (FIX: Composite PK for Multivalued Attribute)
CREATE TABLE DEPARTMENT_LOCATION (
    department_code INT,
    location        VARCHAR(255),
    PRIMARY KEY (department_code, location),
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
    department_code INT,
    join_date       DATE,
    consultation_fee FLOAT DEFAULT 200.0,
    phone           VARCHAR(20),
    license_number  VARCHAR(50) UNIQUE,
    CONSTRAINT chk_doctor_sex CHECK (sex IN ('Male', 'Female', 'Other')),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL
);

-- Circular FK for Chairman
ALTER TABLE DEPARTMENT ADD FOREIGN KEY (chairman_id) REFERENCES DOCTOR(doctor_id) ON DELETE SET NULL;

-- 5. ROOM (Must come before NURSE — NURSE.room_id references ROOM)
CREATE TABLE ROOM (
    room_id         INT PRIMARY KEY AUTO_INCREMENT,
    department_code INT,
    room_number     VARCHAR(20) NOT NULL,
    room_type       VARCHAR(50),
    status          VARCHAR(50) DEFAULT 'available',
    capacity        INT DEFAULT 1,
    UNIQUE (department_code, room_number), -- FIX: Room 101 can exist in multiple departments
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- 6. NURSE
CREATE TABLE NURSE (
    nurse_id        INT PRIMARY KEY,
    name            VARCHAR(100),
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    sex             VARCHAR(10),
    department_code INT,
    room_id         INT,
    phone           VARCHAR(20),
    CONSTRAINT chk_nurse_sex CHECK (sex IN ('Male', 'Female', 'Other')),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL,
    FOREIGN KEY (room_id) REFERENCES ROOM(room_id) ON DELETE SET NULL
);

-- 7. EMPLOYEE
CREATE TABLE EMPLOYEE (
    employee_id     INT PRIMARY KEY,
    name            VARCHAR(100),
    ssn             VARCHAR(20) UNIQUE NOT NULL,
    role            VARCHAR(50),
    department_code INT,
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE SET NULL
);

-- 8. ADMISSION
CREATE TABLE ADMISSION (
    admission_id    INT PRIMARY KEY,
    patient_number  INT,
    department_code INT,
    admission_date  DATE,
    discharge_date  DATE,
    status          VARCHAR(50) DEFAULT 'Active',
    FOREIGN KEY (patient_number)  REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
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
    directions      TEXT,
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

-- 15. USER_ACCOUNT (FIX: Typed Subtype Mapping - Option B)
CREATE TABLE USER_ACCOUNT (
    user_id       INT PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50) UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(50),
    patient_id    INT NULL,
    doctor_id     INT NULL,
    nurse_id      INT NULL,
    employee_id   INT NULL,
    CONSTRAINT chk_single_profile CHECK (
        (CASE WHEN patient_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN doctor_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN nurse_id IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN employee_id IS NOT NULL THEN 1 ELSE 0 END) <= 1
    ),
    FOREIGN KEY (patient_id) REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id)   REFERENCES NURSE(nurse_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id) ON DELETE CASCADE
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
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
    FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id) ON DELETE CASCADE
);

-- 18. GEO_LOCATION (FIX: Composite PK for Multivalued Attribute)
CREATE TABLE GEO_LOCATION (
    department_code INT,
    latitude        FLOAT,
    longitude       FLOAT,
    address         VARCHAR(255),
    PRIMARY KEY (department_code, latitude, longitude),
    FOREIGN KEY (department_code) REFERENCES DEPARTMENT(department_code) ON DELETE CASCADE
);

-- 19. MEDICAL_RECORD (NEW: Requirement 5)
CREATE TABLE MEDICAL_RECORD (
    record_id      INT PRIMARY KEY,
    patient_number INT,
    doctor_id      INT,
    diagnosis      TEXT,
    treatment      TEXT,
    record_date    DATE,
    FOREIGN KEY (patient_number) REFERENCES PATIENT(patient_number) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)      REFERENCES DOCTOR(doctor_id) ON DELETE CASCADE
);

-- ============================================================
-- SAMPLE DATA (ALL USERS CONNECTED)
-- ============================================================

-- 1. DEPARTMENTS
INSERT INTO DEPARTMENT (department_code, name) VALUES 
(1, 'Radiology'), (2, 'Cardiology'), (3, 'Dentistry'), (4, 'Veterinary'), (5, 'Orthopedics');

-- 2. DOCTORS (All 5 Specialists)
INSERT INTO DOCTOR (doctor_id, ssn, name, department_code, consultation_fee, major_area, license_number, sex) VALUES 
(1, 'D101', 'Dr. Ahmed',  1, 300.0, 'Radiologist',        'LIC-001', 'Male'),
(2, 'D102', 'Dr. Sara',   2, 350.0, 'Cardiologist',       'LIC-002', 'Female'),
(3, 'D103', 'Dr. Khaled', 3, 150.0, 'Dentist',            'LIC-003', 'Male'),
(4, 'D104', 'Dr. Layla',  4, 100.0, 'Veterinarian',       'LIC-004', 'Female'),
(5, 'D105', 'Dr. Samir',  5, 250.0, 'Orthopedic Surgeon', 'LIC-005', 'Male');

-- Set Department Chairmen
UPDATE DEPARTMENT SET chairman_id = 1 WHERE department_code = 1;
UPDATE DEPARTMENT SET chairman_id = 2 WHERE department_code = 2;

-- 3. ROOMS
INSERT INTO ROOM (room_id, department_code, room_number, room_type, status, capacity) VALUES 
(1, 1, 'R101', 'Diagnostic',  'Available', 2),
(2, 2, 'R201', 'ICU',         'Occupied',  1),
(3, 3, 'R301', 'General',     'Available', 4),
(4, 5, 'R501', 'Surgery',     'Available', 1);

-- 4. NURSES
INSERT INTO NURSE (nurse_id, ssn, name, sex, department_code, room_id, phone) VALUES
(1, 'N201', 'Nurse Fatma',  'Female', 1, 1, '01011111111'),
(2, 'N202', 'Nurse Hassan', 'Male',   2, 2, '01022222222');

-- 5. EMPLOYEES
INSERT INTO EMPLOYEE (employee_id, ssn, name, role, department_code) VALUES
(1, 'E301', 'Omar Receptionist', 'Receptionist', 1),
(2, 'E302', 'Mona Admin',        'Admin Staff',  2);

-- 6. PATIENTS
INSERT INTO PATIENT (patient_number, ssn, name, medical_history, blood_pressure, heart_rate, temperature, blood_type, sex) VALUES 
(1001, 'P1001', 'Ali Mohamed',   'Hypertension, Seasonal Allergies', 120.8, 72.0, 37.0, 'A+',  'Male'),
(1002, 'P1002', 'Nour Ibrahim',  'Diabetes Type 2',                  130.0, 80.0, 36.8, 'O+',  'Female'),
(1003, 'P1003', 'Youssef Karim', 'No known conditions',              118.5, 68.0, 37.1, 'B-',  'Male');

-- 7. USER ACCOUNTS (ALL ROLES CONNECTED via Option B Typed FKs)
INSERT INTO USER_ACCOUNT (user_id, username, email, password_hash, role, patient_id, doctor_id, nurse_id, employee_id) VALUES
(1,  'admin',       'admin@hospital.com',   'admin123', 'Admin',    NULL, NULL, NULL, NULL),
(2,  'patient_ali', 'ali@email.com',        'pass123',  'Patient',  1001, NULL, NULL, NULL),
(3,  'patient_nour','nour@email.com',       'pass123',  'Patient',  1002, NULL, NULL, NULL),
(4,  'patient_youssef','youssef@email.com', 'pass123',  'Patient',  1003, NULL, NULL, NULL),
(5,  'dr_ahmed',    'ahmed@hospital.com',   'pass123',  'Doctor',   NULL, 1,    NULL, NULL),
(6,  'dr_sara',     'sara@hospital.com',    'pass123',  'Doctor',   NULL, 2,    NULL, NULL),
(7,  'dr_khaled',   'khaled@hospital.com',  'pass123',  'Doctor',   NULL, 3,    NULL, NULL),
(8,  'dr_layla',    'layla@hospital.com',   'pass123',  'Doctor',   NULL, 4,    NULL, NULL),
(9,  'dr_samir',    'samir@hospital.com',   'pass123',  'Doctor',   NULL, 5,    NULL, NULL),
(10, 'nurse_fatma', 'fatma@hospital.com',   'pass123',  'Nurse',    NULL, NULL, 1,    NULL),
(11, 'nurse_hassan','hassan@hospital.com',  'pass123',  'Nurse',    NULL, NULL, 2,    NULL),
(12, 'emp_omar',    'omar@hospital.com',    'pass123',  'Employee', NULL, NULL, NULL, 1),
(13, 'emp_mona',    'mona@hospital.com',    'pass123',  'Employee', NULL, NULL, NULL, 2);

-- 8. APPOINTMENTS
INSERT INTO APPOINTMENT (appointment_id, patient_number, doctor_id, scheduled_at, status, fee, payment_status) VALUES
(1, 1001, 1, '2026-05-10 10:00:00', 'Scheduled',  300.0, 'Paid'),
(2, 1002, 2, '2026-05-11 14:00:00', 'Scheduled',  350.0, 'Paid'),
(3, 1003, 5, '2026-05-12 09:00:00', 'Completed',  250.0, 'Paid'),
(4, 1001, 3, '2026-04-20 11:00:00', 'Completed',  150.0, 'Paid');

-- 9. ADMISSIONS
INSERT INTO ADMISSION (admission_id, patient_number, department_code, admission_date, discharge_date, status) VALUES
(1, 1002, 2, '2026-05-05', NULL, 'Active');

-- 10. EXAMINES (Doctor-Patient M:N)
INSERT INTO EXAMINES (doctor_id, patient_number, hours_per_week) VALUES
(1, 1001, 3), (2, 1002, 5), (5, 1003, 2), (3, 1001, 1);

-- 11. MEDICATIONS
INSERT INTO MEDICATION (medication_id, name, description) VALUES
(1, 'Amoxicillin',  'Antibiotic for bacterial infections'),
(2, 'Metformin',    'Blood sugar control for Type 2 Diabetes'),
(3, 'Ibuprofen',    'Anti-inflammatory and pain relief');

-- 12. PRESCRIPTIONS
INSERT INTO PRESCRIPTION (prescription_id, doctor_id, patient_number, prescription_date) VALUES
(1, 1, 1001, '2026-04-20'),
(2, 2, 1002, '2026-05-05');

-- 13. PRESCRIPTION_MEDICATION
INSERT INTO PRESCRIPTION_MEDICATION (prescription_id, medication_id, times_per_day, dose, directions, start_date, end_date) VALUES
(1, 1, 3, '500mg', 'Take after meals with water', '2026-04-20', '2026-04-30'),
(2, 2, 2, '850mg', 'Take before breakfast and dinner', '2026-05-05', '2026-06-05');

-- 14. DEPARTMENT LOCATIONS
INSERT INTO DEPARTMENT_LOCATION (department_code, location) VALUES
(1, 'Building A - Floor 2'), (1, 'Building A - Floor 3'),
(2, 'Building B - Floor 1'), (3, 'Building C - Floor 1');

-- 15. CONTACT FORM / FEEDBACK
INSERT INTO CONTACT_FORM (form_id, user_id, subject, message, rating, submitted_at, status) VALUES
(1, 2, 'Great Service',      'Dr. Ahmed was very professional.',     5, '2026-05-01 10:00:00', 'Resolved'),
(2, 3, 'Long Wait Time',     'Had to wait 2 hours for my checkup.',  2, '2026-05-03 15:00:00', 'Pending'),
(3, 4, 'Clean Facilities',   'Hospital was very clean and modern.',  4, '2026-05-06 09:00:00', 'Pending');

-- ============================================================
-- REPORT VIEWS
-- ============================================================

CREATE VIEW vw_AppointmentReport AS
SELECT a.appointment_id, p.name AS PatientName, d.name AS DoctorName, dep.name AS DeptName, a.scheduled_at, a.status, a.fee, a.payment_status
FROM APPOINTMENT a 
JOIN PATIENT p ON a.patient_number = p.patient_number 
JOIN DOCTOR d ON a.doctor_id = d.doctor_id 
JOIN DEPARTMENT dep ON d.department_code = dep.department_code;

CREATE VIEW vw_RoomAllocation AS
SELECT r.room_number, r.room_type, dep.name AS DeptName, r.status, p.name AS CurrentPatient, adm.admission_date
FROM ROOM r 
JOIN DEPARTMENT dep ON r.department_code = dep.department_code 
LEFT JOIN ADMISSION adm ON r.department_code = adm.department_code AND adm.discharge_date IS NULL
LEFT JOIN PATIENT p ON adm.patient_number = p.patient_number;

CREATE VIEW vw_DoctorPatientHours AS
SELECT d.name AS DoctorName, p.name AS PatientName, e.hours_per_week
FROM DOCTOR d 
JOIN EXAMINES e ON d.doctor_id = e.doctor_id
JOIN PATIENT p ON e.patient_number = p.patient_number;
