#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import re
import threading
import os
import logging
import json

# These imports assume you have scheduler/feasibility files:
from scheduling.scheduler import schedule_sessions as run_schedule
from scheduling.feasibility_checker import run_feasibility_check

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

# ----------------------------------------------------
# Helper: Validate "HH:MM:SS" format (for durations)
# ----------------------------------------------------
def is_valid_duration(duration):
    if not duration:
        return False
    duration = duration.strip()
    pattern = r'^\d{1,2}:\d{2}:\d{2}$'  # Allows 1 or 2 digits for hours
    return re.match(pattern, duration) is not None

# ----------------------------------------------------
# Utility: Convert timedelta -> "HH:MM"
# ----------------------------------------------------
def convert_timedelta_to_hhmm(td):
    """
    Converts a datetime.timedelta to "HH:MM" string.
    For example, 8 hours => "08:00"
    """
    if not td:
        return "00:00"
    total_seconds = int(td.total_seconds())  # e.g. 28800 for 8:00
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

# ----------------------------------------------------
# Query: Fetch joined data for Timetable
# ----------------------------------------------------
def fetch_sessions_join_schedule():
    """
    Pulls data from SessionAssignments + SessionSchedule to produce a
    combined row for each session:
      {
         SessionID, CourseCode, SessionType,
         Lecturer, DayOfWeek, StartTime, EndTime, RoomName, ...
      }
    We convert TIME columns (StartTime/EndTime) from timedelta to "HH:MM".
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
      SELECT sa.SessionID, sa.CourseCode, sa.SessionType,
             sa.LecturerName AS Lecturer,
             sc.DayOfWeek, sc.StartTime, sc.EndTime, sc.RoomName
      FROM SessionAssignments sa
      JOIN SessionSchedule sc ON sa.SessionID = sc.SessionID
      ORDER BY sa.SessionID
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert TIME fields from timedelta to "HH:MM"
    for r in rows:
        start_td = r["StartTime"]  # e.g. datetime.timedelta
        end_td   = r["EndTime"]
        r["StartTime"] = convert_timedelta_to_hhmm(start_td)
        r["EndTime"]   = convert_timedelta_to_hhmm(end_td)

    return rows

# ----------------------------------------------------
# ROUTE 1: Lecturers
# ----------------------------------------------------
@app.route('/lecturers', methods=['GET', 'POST'])
def lecturers():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_lecturers = request.form.getlist('lecturer_ids')
        # Optionally store them in session
        session['active_lecturers'] = selected_lecturers
        
        # Reset all to inactive, then set chosen ones active
        cursor.execute("UPDATE Lecturer SET ActiveFlag = 0")
        if selected_lecturers:
            placeholders = ','.join(['%s'] * len(selected_lecturers))
            sql = f"UPDATE Lecturer SET ActiveFlag = 1 WHERE LecturerID IN ({placeholders})"
            cursor.execute(sql, tuple(selected_lecturers))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('rooms'))

    # GET: show all lecturers
    cursor.execute("SELECT LecturerID, LecturerName FROM Lecturer")
    lecturers_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lecturers.html', lecturers=lecturers_data)

# ----------------------------------------------------
# ROUTE 2: Rooms
# ----------------------------------------------------
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_rooms = request.form.getlist('room_ids')
        session['active_rooms'] = selected_rooms

        cursor.execute("UPDATE Room SET ActiveFlag = 0")
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

# ----------------------------------------------------
# ROUTE 3: Assign Sessions (Populate SessionAssignments)
# ----------------------------------------------------
@app.route('/assign_sessions', methods=['GET', 'POST'])
def assign_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        session_count = int(request.form.get('session_count', 0))
        course_id = request.form.get('current_course_id')

        # Map CourseID to CourseCode
        cursor.execute("SELECT CourseCode FROM Course WHERE CourseID = %s AND ActiveFlag = 1", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            flash("Invalid or inactive course selected.")
            cursor.close()
            conn.close()
            return redirect(url_for('assign_sessions'))
        course_code = course_row[0]

        for i in range(session_count):
            cohort_name = request.form.get(f'cohort_name_{i}', '').strip()
            lecturer_main = request.form.get(f'lecturer_main_name_{i}_{course_code}', '').strip()
            lecturer_intern = request.form.get(f'lecturer_intern_name_{i}_{course_code}', '').strip()
            session_type = request.form.get(f'session_type_{i}', '').strip()
            duration_str = request.form.get(f'duration_{i}', '').strip()
            enrollments = request.form.get(f'enrollments_{i}', '0').strip()

            # Validation
            if not all([cohort_name, lecturer_main, session_type, duration_str]):
                flash(f"Missing data for session {i+1}. Fill all fields.")
                continue

            if not is_valid_duration(duration_str):
                flash(f"Invalid duration format: {duration_str} (use HH:MM:SS).")
                continue

            try:
                enrollments = int(enrollments)
            except ValueError:
                enrollments = 0

            # Choose which lecturer
            if session_type.lower() == 'discussion' and lecturer_intern:
                chosen_lecturer = lecturer_intern
            else:
                chosen_lecturer = lecturer_main

            # Insert into SessionAssignments
            insert_sql = """
                INSERT INTO SessionAssignments
                (CourseCode, LecturerName, CohortName, SessionType, Duration, NumberOfEnrollments)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                course_code,
                chosen_lecturer,
                cohort_name,
                session_type,
                duration_str,
                enrollments
            ))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Sessions saved for the selected course!")
        return redirect(url_for('assign_sessions'))

    # GET portion
    cursor.execute("SELECT CourseID, CourseCode, CourseName, Credits FROM Course WHERE ActiveFlag = 1")
    courses_data = cursor.fetchall()

    cursor.execute("SELECT LecturerName FROM Lecturer WHERE ActiveFlag = 1")
    lecturers_data = cursor.fetchall()

    cursor.execute("SELECT DISTINCT SessionType FROM SessionAssignments")
    session_types_raw = cursor.fetchall()
    session_types_data = [row[0] for row in session_types_raw] if session_types_raw else ['Lecture','Discussion']

    cursor.execute("SELECT DISTINCT Duration FROM SessionAssignments")
    durations_raw = cursor.fetchall()
    durations_data = [str(row[0]) for row in durations_raw] if durations_raw else ['01:00:00','01:30:00']

    cursor.close()
    conn.close()

    return render_template(
        'assign_sessions.html',
        courses=courses_data,
        lecturers=lecturers_data,
        session_types=session_types_data,
        durations=durations_data
    )

# ----------------------------------------------------
# ROUTE 4: Run Scheduler
# ----------------------------------------------------
@app.route('/run_scheduler', methods=['GET', 'POST'])
def run_scheduler_route():
    if request.method == 'POST':
        session_csv = os.path.join(os.path.dirname(__file__), 'scheduling', 'Session_Location_Preferences.csv')
        try:
            scheduler_thread = threading.Thread(target=run_schedule, args=(session_csv,))
            scheduler_thread.start()
            flash("Scheduling started in the background.")
            logging.info("Scheduler thread started.")
        except Exception as e:
            flash(f"Error scheduling: {e}")
            logging.error(f"Scheduler failed: {e}")
        return redirect(url_for('summary'))
    
    return render_template('run_scheduler.html')

# ----------------------------------------------------
# ROUTE 5: Summary Page
# ----------------------------------------------------
@app.route('/summary')
def summary():
    conn = get_db_connection()
    if conn is None:
        flash("Failed DB connection.")
        return redirect(url_for('home'))
    cursor = conn.cursor()

    query = """
        SELECT sc.ScheduleID,
            s.SessionID,
            s.CourseCode,
            s.LecturerName,
            s.SessionType,
            sc.DayOfWeek,
            sc.StartTime,
            sc.EndTime,
            sc.RoomName
        FROM SessionSchedule sc
        JOIN SessionAssignments s ON sc.SessionID = s.SessionID
        ORDER BY s.SessionID
    """
    try:
        cursor.execute(query)
        assignments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"DB query failed: {err}")
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    cursor.close()
    conn.close()
    return render_template('summary.html', assignments=assignments)

# ----------------------------------------------------
# Home Page
# ----------------------------------------------------
@app.route('/')
def home():
    # Return a landing page or redirect to 'lecturers' or something
    return render_template('index.html')

# ----------------------------------------------------
# Route: Course Selection
# ----------------------------------------------------
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        selected_course_ids = request.form.getlist('course_ids')
        session['selected_courses'] = selected_course_ids
        cursor.close()
        conn.close()
        return redirect(url_for('assign_sessions'))

    cursor.execute("""
        SELECT CourseID, CourseCode, CourseName, Credits
        FROM Course
        WHERE ActiveFlag = 1
    """)
    courses_data = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('courses.html', courses=courses_data)

# ----------------------------------------------------
# Feasibility Check
# ----------------------------------------------------
@app.route('/feasibility', methods=['GET'])
def feasibility():
    results = run_feasibility_check()

    # Build a {MajorID: MajorName}
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT MajorID, MajorName FROM Major")
    majors = cursor.fetchall()
    major_map = {m['MajorID']: m['MajorName'] for m in majors}
    cursor.close()
    conn.close()

    for r in results:
        r['MajorName'] = major_map.get(r['MajorID'], 'Unknown Major')

    return render_template('feasibility.html', results=results)

# ----------------------------------------------------
# Route: Student->Courses bridging
# ----------------------------------------------------
@app.route('/student_courses', methods=['GET', 'POST'])
def student_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        selected_codes = request.form.getlist('course_codes')

        # Overwrite old rows
        cursor.execute("DELETE FROM StudentCourseSelection WHERE StudentID = %s", (student_id,))
        insert_sql = """
            INSERT INTO StudentCourseSelection (StudentID, CourseCode)
            VALUES (%s, %s)
        """
        for ccode in selected_codes:
            cursor.execute(insert_sql, (student_id, ccode))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Courses updated successfully!")
        return redirect(url_for('student_courses'))

    # GET: fetch students
    cursor.execute("SELECT StudentID, MajorID, YearNumber FROM Student")
    students_data = cursor.fetchall()

    # fetch courses
    cursor.execute("""
        SELECT CourseCode, CourseName
        FROM Course
        WHERE ActiveFlag = 1
        ORDER BY CourseCode
    """)
    courses_data = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student_courses.html',
                           students=students_data,
                           courses=courses_data)

# ----------------------------------------------------
# Timetable Page (Drag-and-Drop UI)
# ----------------------------------------------------
@app.route('/timetable', methods=['GET'])
def timetable():
    """
    Renders timetable with session data from SessionSchedule + SessionAssignments.
    """
    sessions = fetch_sessions_join_schedule()
    return render_template('timetable.html', sessions=sessions)

# ----------------------------------------------------
# Check Conflict (Drag-and-Drop)
# ----------------------------------------------------
@app.route('/check_conflict', methods=['POST'])
def check_conflict():
    data = request.json
    session_id = data.get("SessionID")
    new_day = data.get("NewDay")
    new_start = data.get("NewStartTime")

    # Here is where you'd do real checks for overlapping with same lecturer or same cohort
    conflict_found = False
    reason = ""

    return jsonify({"conflict": conflict_found, "reason": reason})

# ----------------------------------------------------
# Save Timetable (Drag-and-Drop)
# ----------------------------------------------------
@app.route('/save_timetable', methods=['POST'])
def save_timetable():
    data = request.json  # array of {SessionID, DayOfWeek, StartTime, EndTime}
    conn = get_db_connection()
    cursor = conn.cursor()

    for sess in data:
        sid = sess["SessionID"]
        day = sess["DayOfWeek"]
        start = sess["StartTime"]
        end = sess["EndTime"]
        sql = """
          UPDATE SessionSchedule
          SET DayOfWeek=%s, StartTime=%s, EndTime=%s
          WHERE SessionID=%s
        """
        cursor.execute(sql, (day, start, end, sid))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Timetable saved successfully"})

if __name__ == '__main__':
    app.run(debug=True)