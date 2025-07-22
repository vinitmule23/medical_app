from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from datetime import datetime, time, timedelta

app = Flask(__name__)

# Configure MySQL connection
db = mysql.connector.connect(
    host="127.0.0.2",
    user="root",
    password="Vinit@2772",
    database="medical_db2"
)
cursor = db.cursor(dictionary=True)

# Home page with form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        diagnosis = request.form['diagnosis']
        address = request.form['address']
        medicines = request.form['medicines']
        medical_history = request.form['medical_history']

        sql = "INSERT INTO patients (name, age, gender, diagnosis, address, medicines, medical_history) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (name, age, gender, diagnosis, address, medicines, medical_history)
        cursor.execute(sql, val)
        db.commit()

        return "Patient record added successfully!"
    
    return render_template('form.html')

# Search patient by ID
@app.route('/view', methods=['GET', 'POST'])
def view():
    patient = None
    if request.method == 'POST':
        pid = request.form['patient_id']
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (pid,))
        patient = cursor.fetchone()

    return render_template('view.html', patient=patient)

# Appointments routes
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        reason = request.form['reason']
        
        try:
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            return "Invalid date or time format", 400

        sql = """INSERT INTO appointments 
                (patient_id, appointment_date, appointment_time, reason) 
                VALUES (%s, %s, %s, %s)"""
        val = (patient_id, appointment_date, appointment_time, reason)
        cursor.execute(sql, val)
        db.commit()

        return redirect(url_for('view_appointments'))
    
    cursor.execute("SELECT patient_id, name FROM patients ORDER BY name")
    patients = cursor.fetchall()
    return render_template('appointments.html', patients=patients)

@app.route('/view-appointments')
def view_appointments():
    cursor.execute("""
        SELECT a.appointment_id, a.patient_id, p.name as patient_name, 
               a.appointment_date, a.appointment_time, a.reason, a.status
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.patient_id
        ORDER BY a.appointment_date, a.appointment_time
    """)
    appointments = cursor.fetchall()

    for appt in appointments:
        if isinstance(appt['appointment_time'], timedelta):
            # Convert timedelta to time by getting total seconds and creating a time object
            total_seconds = appt['appointment_time'].total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            appt['appointment_time'] = time(hour=hours, minute=minutes)
    
    return render_template('view_appointments.html', appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)
