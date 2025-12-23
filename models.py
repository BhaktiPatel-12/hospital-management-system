from datetime import datetime
from enum import Enum
from config import db

class Patient(db.Model):
    patient_id = db.Column(db.String(10), primary_key=True)
    patient_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(8), nullable=False)
    email = db.Column(db.String(30), nullable=True)
    contact_no = db.Column(db.String(10),  nullable=True)

class Doctor(db.Model):
    doctor_id = db.Column(db.String(10), primary_key=True)
    doctor_name = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)

    department = db.relationship('Department', backref='doctors')

class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(80), nullable=False)
    department_description = db.Column(db.String(100), nullable=False)
    doctors_registered = db.Column(db.Integer, nullable=False)

class Treatment(db.Model):
    patient_id = db.Column(db.String(10), db.ForeignKey('patient.patient_id'), nullable=False, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=False, primary_key=True)
    test_done = db.Column(db.String(100), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    prescription = db.Column(db.String(200), nullable=False)
    medicines = db.Column(db.String(300), nullable=False)

class Appointment_status(Enum):
    Booked = "booked"
    Cancelled = "cancelled"
    Completed = "completed"

class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(10), db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_name = db.Column(db.String(30), db.ForeignKey('doctor.doctor_name'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(30), nullable=False)
    status = db.Column(db.Enum(Appointment_status), nullable=False, default=Appointment_status.Booked)

departments = [
    (1001, "Eyes", "Vision-related problems and diseases.", 2),
    (1002, "ENT", "Ear, nose, and throat related conditions.", 2),
    (1003, "Dentist", "Dental care and oral health.", 3),
    (1004, "Orthopedic", "Bone, joint, and musculoskeletal disorders.", 4),
    (1005, "Cardiologist", "Heart and cardiovascular diseases.", 4),
    (1006, "Pulmonologist", "Lung and respiratory issues.", 2),
    (1007, "Oncologist", "Cancer diagnosis and treatment.", 3),
    (1008, "MD Physician", "General medical care and treatment.", 4),
    (1009, "Gastroenterologist", "Digestive system diseases.", 3),
    (1010, "Neurologist", "Nervous system and brain disorders.", 4),
]

doctors = [
    ("D001", "Dr. Ashok K. Patel", 1001, "Cataract Surgery,Glaucoma Treatment"),
    ("D002", "Dr. Mihir M. Patel", 1001, "Retina and Uvea Diseases, Lasik Surgery"),
    ("D003", "Dr. Bharat Vyas", 1002, "Cochlear Implants, ENT Surgery"),
    ("D004", "Dr. Ketan Shah", 1002, "Throat Cancer, Hearing Loss"),
    ("D005", "Dr. Bhavin B. Patel", 1003, "Cosmetic Dentistry, Implants"),
    ("D006", "Dr. Rupal Desai", 1003, "Implantology"),
    ("D007", "Dr. Kaushik Patel", 1003, "Tooth Surgery Expert"),
    ("D008", "Dr. Hitesh Chawda", 1004, "Joint Replacement Surgery"),
    ("D009", "Dr. Viral Ghandhi", 1004, "Best Orthopedic Surgery Expert"),
    ("D010", "Dr. Prathmesh K. Shah", 1004, "Spine Surgery, Trauma, and Sports Injuries"),
    ("D011", "Dr. Vishal Modi", 1004, "Orthopedic surgery, spine surgery, sports injuries"),
    ("D012", "Dr. Devang M. Patel", 1005, "Interventional Cardiology, Heart Disease Treatment"),
    ("D013", "Dr. Nirav Shah", 1005, "Cardiac Surgery, Angioplasty, Heart Disease Prevention"),
    ("D014", "Dr. Tejas Patel", 1005, "Best Robotic Cardio Surgery Expert all over India"),
    ("D015", "Dr. Shalin Mehta", 1005, "Cardiac electrophysiology, Interventional cardiology"),
    ("D016", "Dr. Chirag B. Patel", 1006, "Asthma, COPD, Sleep Apnea"),
    ("D017", "Dr. Samir Shah", 1006, "Pulmonary Diseases, Chest Infections"),
    ("D018", "Dr. Manish N. Shah", 1007, "Medical Oncology , Chemotherapy Expert"),
    ("D019", "Dr. Kirti Patel", 1007, "Breast Cancer Surgeon , Chemotheraphy Expert"),
    ("D020", "Dr. Niraj Gupta", 1007, "Surgical Oncology , Cancer Surgery"),
    ("D021", "Dr. Shital J. Mehta", 1008, "General Medicine , Preventive Health CheckUps"),
    ("D022", "Dr. Mitesh Shah", 1008, "Internal Medicine , Regular CheckUps"),
    ("D023", "Dr. Rajesh Shah", 1008, "General Medicine"),
    ("D024", "Dr. Pragnesh Patel", 1008, "General Medicine, Diabetes, Asthma"),
    ("D025", "Dr. Alok Vyas", 1009, "Hepatology , Gastrointestinal Endoscopy"),
    ("D026", "Dr. Sandeep Patel", 1009, "Gastroenterology , Liver Transplant"),
    ("D027", "Dr. Kunal Shah", 1010, "Epilepsy , Stroke , Neurocritical Care"),
    ("D028", "Dr. Nirav Shukla", 1010, "Neuroimmunology, Stroke, Movement Disorders"),
    ("D029", "Dr. Bhagaynadan Patel", 1010, "SuperSpecialist Neurology"),
    ("D030", "Dr. Amit Desai", 1010, "Neurology, Stroke, Neurodegenerative diseases"),
]

def insert_departments():
    for dep_id, name, desc, count in departments:
        if not Department.query.filter_by(department_id=dep_id).first():
            db.session.add(Department(
                department_id=dep_id,
                department_name=name,
                department_description=desc,
                doctors_registered=count
            ))
            db.session.commit()

def insert_doctors():
    for did, dname, dep, spec in doctors:
        if not Doctor.query.filter_by(doctor_id=did).first():
            db.session.add(Doctor(
                doctor_id=did,
                doctor_name=dname,
                department_id=dep,
                specialization=spec
            ))
            db.session.commit()