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
        course_id = request.form.get('current_course_id')

        for i in range(session_count):
            # Reading the posted fields:
            # 'cohort_name_i' is a text field we auto-filled with "Section A," "Section B," etc.
            cohort_name = request.form.get(f'cohort_name_{i}', '')
            lecturer_main_id = request.form.get(f'lecturer_main_id_{i}_{course_id}')
            lecturer_intern_id = request.form.get(f'lecturer_intern_id_{i}_{course_id}')
            session_type_id = request.form.get(f'session_type_id_{i}')
            duration_id = request.form.get(f'duration_id_{i}')
            enrollments = request.form.get(f'enrollments_{i}', '0')

            # Convert enrollments to integer
            enrollments = int(enrollments) if enrollments else 0

            # Decide which lecturer to store 
            chosen_lecturer = lecturer_main_id  # or logic if session_type = Discussion => lecturer_intern_id

            # Look up the CohortID matching the cohort_name
            # e.g., if cohort_name='Section A' => CohortID=1 in the table
            # If not found, you can handle logic or skip
            cursor.execute("SELECT CohortID FROM Cohort WHERE CohortName = %s", (cohort_name,))
            row = cursor.fetchone()
            if row:
                actual_cohort_id = row[0]
            else:
                # If not found, you could either skip or insert a new row. We'll skip here
                actual_cohort_id = None

            if actual_cohort_id:
                # Insert a new row in SessionAssignments
                sql_insert = """
                    INSERT INTO SessionAssignments
                    (CourseID, LecturerID, CohortID, SessionTypeID, DurationID, NumberOfEnrollments)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (
                    course_id,
                    chosen_lecturer,
                    actual_cohort_id,
                    session_type_id,
                    duration_id,
                    enrollments
                ))
            else:
                # If you prefer to handle missing "Section X" in your Cohort table:
                # flash(f"Cohort '{cohort_name}' not found. Skipped row.")
                pass

        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Sessions saved successfully for that course!")
        return redirect(url_for('assign_sessions'))

    # GET request => show the page with all courses, etc.
    # Fetch active courses
    cursor.execute("SELECT CourseID, CourseCode, CourseName, Credits FROM Course WHERE ActiveFlag = 1")
    courses_data = cursor.fetchall()

    # Fetch active lecturers
    cursor.execute("SELECT LecturerID, LecturerName FROM Lecturer WHERE ActiveFlag = 1")
    lecturers_data = cursor.fetchall()

    # Session types
    cursor.execute("SELECT SessionTypeID, SessionTypeName FROM SessionType")
    session_types_data = cursor.fetchall()

    # Durations, converting TIME to string
    cursor.execute("SELECT DurationID, Duration FROM Duration")
    durations_raw = cursor.fetchall()
    durations_data = [(row[0], str(row[1])) for row in durations_raw]

    cursor.close()
    conn.close()

    return render_template(
        'assign_sessions.html',
        courses=courses_data,
        lecturers=lecturers_data,
        session_types=session_types_data,
        durations=durations_data
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

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        selected_course_ids = request.form.getlist('course_ids')
        session['selected_courses'] = selected_course_ids  # store in session or handle DB updates
        cursor.close()
        conn.close()
        return redirect(url_for('assign_sessions'))

    # GET: Show all active courses
    cursor.execute("""
        SELECT CourseID, CourseCode, CourseName, Credits
        FROM Course
        WHERE ActiveFlag = 1
    """)
    courses_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('courses.html', courses=courses_data)



if __name__ == '__main__':
    app.run(debug=True)