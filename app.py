from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from config import app, db
from models import (
    Patient, Doctor, Department, Treatment,
    Appointment, Appointment_status,
    insert_departments, insert_doctors
)

# Jinja date filter
@app.template_filter('date')
def date_filter(dt, format='%Y-%m-%d'):
    if isinstance(dt, datetime):
        return dt.strftime(format)
    return dt

# Create tables
with app.app_context():
    db.create_all()
    insert_departments()
    insert_doctors()

#connection to html pages through routing
@app.route('/')
def index():
    return render_template('index.html')

#rendering the html login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin":
            session['user_type'] = "admin"
            session['admin'] = "Admin"
            return redirect(url_for('admin_dashboard'))

        patient = Patient.query.filter_by(patient_name=username, password=password).first()
        if patient:
            session['user_type'] = "patient"
            session['patient_id'] = patient.patient_id
            session['patient_name'] = patient.patient_name
            return redirect(url_for('patient_dashboard'))
        
        doctor = Doctor.query.filter_by(doctor_name=username).first()
        if doctor:
            if username == doctor.doctor_name and password == "doctor":
                session['user_type'] = "doctor"
                session['doctor_id'] = doctor.doctor_id
                session['doctor_name'] = doctor.doctor_name
                return redirect(url_for('doctor_dashboard'))

        # Wrong credentials
        flash('Incorrect username or password!', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

#rendering the html admin page
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    
    total_doctors = len(doctors)
    total_patients = len(patients)
    total_appointments = len(appointments)

    # Include patient object in appointments for table display
    appointments_with_patient = []
    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        appt.patient = patient
        appointments_with_patient.append(appt)

    return render_template(
        'admin.html',
        doctors=doctors,
        patients=patients,
        appointments=appointments_with_patient,
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments
    )

#rendering the html register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_patient = Patient.query.filter_by(patient_name=username).first()
        if existing_patient:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))

        # Auto-generate patient ID (P001, P002...)
        last_patient = Patient.query.order_by(Patient.patient_id.desc()).first()
        if last_patient:
            new_patient_id = 'P' + str(int(last_patient.patient_id[1:]) + 1).zfill(3)
        else:
            new_patient_id = 'P001'

        # Save new patient including password
        new_patient = Patient(
            patient_id=new_patient_id,
            patient_name=username,
            password=password
        )

        try:
            db.session.add(new_patient)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

#rendering the html doctor dashboard
@app.route('/doctor', methods=['GET'])
def doctor_dashboard():
    if session.get('user_type') != "doctor":
        return redirect(url_for('login'))

    doctor_name = session.get('doctor_name')

    # JOIN Appointment with Patient table
    appointments = (
        db.session.query(Appointment, Patient)
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .filter(Appointment.doctor_name == doctor_name)
        .all()
    )

    # Get unique completed patients
    completed_patients = {}
    for appt, patient in appointments:
        if appt.status == Appointment_status.Completed:
            completed_patients[patient.patient_id] = patient

    return render_template(
        'doctor.html',
        doctor_name=doctor_name,
        appointments=appointments,
        completed_patients=completed_patients.values()  # only unique patients
    )

#rendering the html patient dashboard
@app.route('/patient', methods=['GET'])
def patient_dashboard():
    if session.get('user_type') != "patient":
        return redirect(url_for('login'))

    patient_name = session.get('patient_name')

    # Fetch all departments
    departments = Department.query.all()

    return render_template(
        'patient.html',
        patient_name=patient_name,
        departments=departments
    )

#rendering to view doctors
@app.route('/view_doctors/<int:department_id>')
def view_doctors(department_id):

    department = Department.query.get(department_id)
    doctors = Doctor.query.filter_by(department_id=department_id).all()

    return render_template(
        'doctor_list.html',
        department=department,
        doctors=doctors
    )

#rendering to see patient past history
@app.route('/past_history/<string:patient_id>')
def past_history(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('doctor_dashboard'))
    treatments = (
        db.session.query(Treatment, Appointment)
        .join(Appointment, Treatment.appointment_id == Appointment.appointment_id)
        .filter(Treatment.patient_id == patient_id)
        .all()
    )

    return render_template('past_history.html', patient=patient,treatments=treatments)

#rendering to see patient past history from patient dashboard
@app.route('/history/<string:patient_id>')
def history(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('doctor_dashboard'))
    treatments = (
        db.session.query(Treatment, Appointment)
        .join(Appointment, Treatment.appointment_id == Appointment.appointment_id)
        .filter(Treatment.patient_id == patient_id)
        .all()
    )

    return render_template('history.html', patient=patient,treatments=treatments)

#rendering to see patient past history from admin dashboard
@app.route('/patient_history/<string:patient_id>')
def patient_history(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('doctor_dashboard'))
    treatments = (
        db.session.query(Treatment, Appointment)
        .join(Appointment, Treatment.appointment_id == Appointment.appointment_id)
        .filter(Treatment.patient_id == patient_id)
        .all()
    )

    return render_template('patient_history.html', patient=patient,treatments=treatments)

#rendering to view doctor availability in patient dashboard
@app.route('/availability')
def check_availability():
    return render_template('availability.html')

#rendering to view doctor availability in doctor dashboard
@app.route('/doc_availability')
def doctor_availability():
    return render_template('doctor_availability.html')

#render to logout page which will clear session
@app.route('/logout',methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

#rendering to book appointment page
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if session.get('user_type') != "patient":
        return redirect(url_for('login'))
    
    last_appointment = Appointment.query.order_by(Appointment.appointment_id.desc()).first()
    
    if last_appointment:
        new_appointment_id = str(int(last_appointment.appointment_id) + 1)
    else:
        new_appointment_id = '101'

    if request.method == 'POST':
        patient_id = session.get('patient_id')             # Automatically taken from login session
        doctor_name = request.form['doctor_name']
        appointment_date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        appointment_time = request.form['time']

        new_appointment = Appointment(
            appointment_id=new_appointment_id,
            patient_id=patient_id,
            doctor_name=doctor_name,
            date=appointment_date,
            time=appointment_time,
            status=Appointment_status.Booked
        )

        db.session.add(new_appointment)
        db.session.commit()

    # GET request → load doctors list
    doctors = Doctor.query.all()
    return render_template('book_appointment.html', doctors=doctors, today=date.today())

#rendering to view appointment page
@app.route('/view_appointment')
def view_appointment():
    if session.get('user_type') != "patient":
        return redirect(url_for('login'))

    patient_id = session.get('patient_id')

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    return render_template('view_appointment.html', appointments=appointments)

#rendering to cancel appointment
@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    appointment.status = Appointment_status.Cancelled
    db.session.commit()
    return redirect(url_for('view_appointment'))

#rendering to mark as completed appointment
@app.route('/complete_appointment/<int:appointment_id>', methods=['POST'])
def complete_appointment(appointment_id):
    if session.get('user_type') != "doctor":
        return redirect(url_for('login'))

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        flash("Appointment not found!", "error")
        return redirect(url_for('doctor_dashboard'))

    # Update the status
    appointment.status = Appointment_status.Completed
    db.session.commit()

    flash("Appointment marked as completed!", "success")
    return redirect(url_for('doctor_dashboard'))

#rendering to mark as cancel appointment from doctor dashboard
@app.route('/doctor_cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment_by_doctor(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    appointment.status = Appointment_status.Cancelled
    db.session.commit()
    return redirect(url_for('doctor_dashboard'))

#rendering to treatment page to add treatment for patient in doctor dashboard
@app.route('/start_treatment/<int:appointment_id>', methods=['GET', 'POST'])
def start_treatment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        flash("Appointment not found!", "error")
        return redirect(url_for('doctor_dashboard'))

    patient = Patient.query.get(appointment.patient_id)

    if request.method == 'POST':
        test_done = request.form['test_done']
        diagnosis = request.form['diagnosis']
        prescription = request.form['prescription']
        medicines = request.form['medicines']

        # Check if treatment already exists
        existing_treatment = Treatment.query.filter_by(
            patient_id=appointment.patient_id,
            appointment_id=appointment_id
        ).first()

        if existing_treatment:
            # UPDATE query
            existing_treatment.test_done = test_done
            existing_treatment.diagnosis = diagnosis
            existing_treatment.prescription = prescription
            existing_treatment.medicines = medicines
        else:
            # INSERT query
            new_treatment = Treatment(
                patient_id=appointment.patient_id,
                appointment_id=appointment_id,
                test_done=test_done,
                diagnosis=diagnosis,
                prescription=prescription,
                medicines=medicines,
            )
            db.session.add(new_treatment)

        db.session.commit()

        flash("Treatment saved successfully!", "success")
        return redirect(url_for('doctor_dashboard'))

    return render_template(
        'treatment.html',
        appointment=appointment,
        patient=patient
    )

#rendering to edit doctor page
@app.route('/edit_doctor/<string:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash("Doctor not found!", "error")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        doctor.doctor_name = request.form['doctor_name']
        doctor.specialization = request.form['specialization']
        doctor.department_id = request.form['department_id']
        db.session.commit()
        flash("Doctor updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    departments = Department.query.all()
    return render_template('edit_doctor.html', doctor=doctor, departments=departments)

#rendering to delete doctor
@app.route('/delete_doctor/<string:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash("Doctor not found!", "error")
        return redirect(url_for('admin_dashboard'))

    # Delete the doctor
    db.session.delete(doctor)
    db.session.commit()

    flash("Doctor deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

#rendering to edit patient
@app.route('/edit_patient/<string:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        patient.patient_name = request.form['patient_name']
        patient.password = request.form['password']
        db.session.commit()

        flash("Patient updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_patient.html', patient=patient)

#rendering to delete patient
@app.route('/delete_patient/<string:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('admin_dashboard'))

    db.session.delete(patient)
    db.session.commit()

    flash("Patient deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

#rendering to add doctor in admin dashboard
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        department_id = request.form['department_id']
        specialization = request.form['specialization']

        # Auto-generate doctor ID (D001, D002, ...)
        last_doctor = Doctor.query.order_by(Doctor.doctor_id.desc()).first()
        if last_doctor:
            next_id = int(last_doctor.doctor_id[1:]) + 1
            doctor_id = f"D{next_id:03d}"
        else:
            doctor_id = "D001"

        new_doctor = Doctor(
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            department_id=department_id,
            specialization=specialization
        )

        # Increase doctor count in department
        dept = Department.query.get(department_id)
        dept.doctors_registered += 1

        db.session.add(new_doctor)
        db.session.commit()

        flash("Doctor added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    departments = Department.query.all()
    return render_template('add_doctor.html', departments=departments)

#rendering to edit profile for admin dashboard
@app.route('/edit_profile/<string:patient_id>', methods=['GET', 'POST'])
def edit_profile(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('patient_dashboard'))

    if request.method == 'POST':
        patient.patient_name = request.form['patient_name']
        patient.email = request.form['email']
        patient.contact_no = request.form['contact_no']
        patient.password = request.form['password']

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('patient_dashboard'))

    return render_template("edit_profile.html", patient=patient)

#rendering to view patient in admin dashboard
@app.route('/view_patient/<string:patient_id>', methods=['GET'])
def view_patient(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('admin_dashboard'))

    return render_template(
        'view_patient.html',
        patient=patient
    )

# run flask app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)