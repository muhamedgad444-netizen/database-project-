# Hospital Information System — Relational Schema Mapping (Synced with ERD)

## What is Schema Mapping?
This document shows the final table structures as defined in the **hospital_erd.html** diagram and implemented in **hospital_db.sql**.

---

## 1. PATIENT
```
PATIENT ( patient_number [PK], ssn [UK], name, address, phone, birthdate, sex, 
          medical_history, blood_pressure, heart_rate, temperature, blood_type )
```

## 2. DEPARTMENT
```
DEPARTMENT ( department_code [PK], name [UK], chairman_id [FK, UK → DOCTOR], chairman_start_date )
```

## 3. DEPARTMENT_LOCATION
```
DEPARTMENT_LOCATION ( dept_location_id [PK], department_code [FK], location )
```

## 4. DOCTOR
```
DOCTOR ( doctor_id [PK], ssn [UK], name, sex, birth_date, major_area, degree, 
         department_code [FK], join_date, consultation_fee, phone, license_number [UK] )
```

## 5. NURSE
```
NURSE ( nurse_id [PK], name, ssn [UK], sex, department_code [FK], room_id [FK], phone )
```

## 6. EMPLOYEE
```
EMPLOYEE ( employee_id [PK], name, ssn [UK], role, department_code [FK] )
```

## 7. ADMISSION
```
ADMISSION ( admission_id [PK], patient_number [FK], department_code [FK], 
            admission_date, discharge_date, status )
```

## 8. ROOM
```
ROOM ( room_id [PK], department_code [FK], room_number [UK], room_type, status, capacity )
```

## 9. ROOM_RESERVATION
```
ROOM_RESERVATION ( reservation_id [PK], room_id [FK], doctor_id [FK], 
                   patient_number [FK], start_date, end_date )
```

## 10. EXAMINES (M:N Relationship)
```
EXAMINES ( doctor_id [FK], patient_number [FK], hours_per_week )
```

## 11. PRESCRIPTION
```
PRESCRIPTION ( prescription_id [PK], doctor_id [FK], patient_number [FK], prescription_date )
```

## 12. MEDICATION
```
MEDICATION ( medication_id [PK], name, description )
```

## 13. PRESCRIPTION_MEDICATION
```
PRESCRIPTION_MEDICATION ( prescription_id [FK], medication_id [FK], 
                          times_per_day, dose, directions, start_date, end_date )
```

## 14. APPOINTMENT
```
APPOINTMENT ( appointment_id [PK], patient_number [FK], doctor_id [FK], 
              scheduled_at, status, fee, payment_status, refund_date )
```

## 15. USER_ACCOUNT
```
USER_ACCOUNT ( user_id [PK], username [UK], email [UK], password_hash, role, 
               profile_id, profile_type )
```

## 16. SCAN_FILE
```
SCAN_FILE ( scan_id [PK], patient_number [FK], doctor_id [FK], 
            file_path, file_type, uploaded_at, description )
```

## 17. CONTACT_FORM
```
CONTACT_FORM ( form_id [PK], user_id [FK], subject, message, rating, submitted_at, status )
```

## 18. GEO_LOCATION
```
GEO_LOCATION ( location_id [PK], department_code [FK], latitude, longitude, address )
```

## 19. MEDICAL_RECORD (Requirement 5)
```
MEDICAL_RECORD ( record_id [PK], patient_number [FK], doctor_id [FK], diagnosis, treatment, record_date )
```
