from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector  # <-- Using MySQL connector now

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Needed for session usage

# ----------------------------------------------------
# MySQL Database Connection
# ----------------------------------------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Naakey057@',
        database='schedulai'
    )
    return conn

# --------------------------------------------
# 1. First Page: Select Active Lecturers
# --------------------------------------------
@app.route('/lecturers', methods=['GET', 'POST'])
def lecturers():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_lecturers = request.form.getlist('lecturer_ids')
        # Store them in session (optional)
        session['active_lecturers'] = selected_lecturers
        
        # Optionally, update the DB to mark them active
        cursor.execute("UPDATE Lecturer SET ActiveFlag = 0")  # reset all to 0
        if selected_lecturers:
            # MySQL uses %s placeholders
            placeholders = ','.join(['%s'] * len(selected_lecturers))
            sql = f"UPDATE Lecturer SET ActiveFlag = 1 WHERE LecturerID IN ({placeholders})"
            cursor.execute(sql, tuple(selected_lecturers))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('rooms'))

    # GET request: show all lecturers
    cursor.execute("SELECT LecturerID, LecturerName FROM Lecturer")
    lecturers_data = cursor.fetchall()
    
    # Because fetchall() returns tuples, you can pass them directly, 
    # or convert to a list of dicts if desired:
    # e.g.: lecturers_data = [{'LecturerID': row[0], 'LecturerName': row[1]} for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    return render_template('lecturers.html', lecturers=lecturers_data)

# --------------------------------------------
# 2. Second Page: Select Active Rooms
# --------------------------------------------
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_rooms = request.form.getlist('room_ids')
        session['active_rooms'] = selected_rooms
        
        cursor.execute("UPDATE Room SET ActiveFlag = 0")  # reset all to 0
        if selected_rooms:
            placeholders = ','.join(['%s'] * len(selected_rooms))
            sql = f"UPDATE Room SET ActiveFlag = 1 WHERE RoomID IN ({placeholders})"
            cursor.execute(sql, tuple(selected_rooms))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('assign_sessions'))

    # GET: show rooms
    cursor.execute("SELECT RoomID, Location, MaxRoomCapacity FROM Room")
    rooms_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('rooms.html', rooms=rooms_data)

# --------------------------------------------
# 3. Third Page: Populate Session Assignments
# --------------------------------------------
@app.route('/assign_sessions', methods=['GET', 'POST'])
def assign_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        session_count = int(request.form.get('session_count', 0))
        
        for i in range(session_count):
            course_id = request.form.get(f'course_id_{i}')
            lecturer_id = request.form.get(f'lecturer_id_{i}')
            cohort_id = request.form.get(f'cohort_id_{i}')
            session_type_id = request.form.get(f'session_type_id_{i}')
            duration_id = request.form.get(f'duration_id_{i}')
            
            if course_id and lecturer_id and cohort_id and session_type_id and duration_id:
                sql_insert = """
                    INSERT INTO SessionAssignments
                    (CourseID, LecturerID, CohortID, SessionTypeID, DurationID)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (course_id, lecturer_id, cohort_id, session_type_id, duration_id))

        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Session assignments saved successfully!')
        return redirect(url_for('assign_sessions'))

    # GET: show data for the assignment form
    cursor.execute("SELECT CourseID, CourseCode, CourseName FROM Course WHERE ActiveFlag = 1")
    courses_data = cursor.fetchall()

    cursor.execute("SELECT LecturerID, LecturerName FROM Lecturer WHERE ActiveFlag = 1")
    active_lecturers = cursor.fetchall()

    cursor.execute("SELECT CohortID, CohortName FROM Cohort")
    cohorts = cursor.fetchall()

    cursor.execute("SELECT SessionTypeID, SessionTypeName FROM SessionType")
    session_types = cursor.fetchall()

    cursor.execute("SELECT DurationID, Duration FROM Duration")
    durations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'assign_sessions.html',
        courses=courses_data,
        lecturers=active_lecturers,
        cohorts=cohorts,
        session_types=session_types,
        durations=durations
    )

# --------------------------------------------
# Summary Page
# --------------------------------------------
@app.route('/summary')
def summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.SessionID,
               c.CourseCode,
               l.LecturerName,
               co.CohortName,
               st.SessionTypeName,
               d.Duration
        FROM SessionAssignments s
        JOIN Course c ON s.CourseID = c.CourseID
        JOIN Lecturer l ON s.LecturerID = l.LecturerID
        JOIN Cohort co ON s.CohortID = co.CohortID
        JOIN SessionType st ON s.SessionTypeID = st.SessionTypeID
        JOIN Duration d ON s.DurationID = d.DurationID
        ORDER BY s.SessionID ASC
    """
    cursor.execute(query)
    assignments = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('summary.html', assignments=assignments)
@app.route('/')
def home():
    # Option A: Return a template if you want a custom landing page
    return render_template('index.html')

    # Option B: Redirect to lecturers (if that's your "first page")
    # return redirect(url_for('lecturers'))


if __name__ == '__main__':
    app.run(debug=True)