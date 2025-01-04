#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import re
import threading
import os
import logging
import json

# These imports assume you have the following local modules:
from scheduling.scheduler import schedule_sessions as run_schedule
from scheduling.feasibility_checker import run_feasibility_check

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Needed for session usage

# ----------------------------------------------------
# MySQL Database Connection
# ----------------------------------------------------
def get_db_connection():
    """
    Connects to your schedulai database using mysql.connector.
    Adjust host/user/password if needed.
    """
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
    pattern = r'^\d{1,2}:\d{2}:\d{2}$'  # Allows 1-2 digits for HH
    return re.match(pattern, duration) is not None

# ----------------------------------------------------
# Utility: Convert timedelta -> "HH:MM"
# ----------------------------------------------------
def convert_timedelta_to_hhmm(td):
    """
    Converts a datetime.timedelta to "HH:MM" string, e.g. 8 hours -> "08:00"
    """
    if not td:
        return "00:00"
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

# ----------------------------------------------------
# HELPER A: Overlap check for Friday 11:50–12:15
# ----------------------------------------------------
def overlaps_friday_prayer(day_of_week, start_str, end_str):
    """
    Returns True if the requested day/time overlaps with
    Friday prayer (11:50–12:15). Otherwise False.
    """
    if day_of_week.lower() != 'friday':
        return False  # Only relevant on Friday

    def parse_hhmm_to_minutes(hhmm):
        hh, mm = hhmm.split(':')
        return int(hh)*60 + int(mm)

    requested_start = parse_hhmm_to_minutes(start_str)
    requested_end   = parse_hhmm_to_minutes(end_str)

    prayer_start = parse_hhmm_to_minutes("11:50")
    prayer_end   = parse_hhmm_to_minutes("12:15")

    # Overlap condition
    return (requested_start < prayer_end) and (requested_end > prayer_start)

# ----------------------------------------------------
# HELPER B: Which days is a lecturer assigned?
# ----------------------------------------------------
def lecturer_assigned_days(lecturer_name):
    """
    Returns a set of distinct days (e.g. {"Monday","Wednesday"})
    the lecturer is currently scheduled for.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT DISTINCT ss.DayOfWeek AS day
        FROM SessionSchedule ss
        JOIN SessionAssignments sa ON ss.SessionID = sa.SessionID
        WHERE sa.LecturerName = %s
    """
    cursor.execute(sql, (lecturer_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {row['day'] for row in rows}

# ----------------------------------------------------
# Check Room Availability (with Friday constraint)
# ----------------------------------------------------
def rooms_free_for_timeslot(day_of_week, start_time_str, end_time_str):
    """
    Returns a list of (RoomID, Location, MaxRoomCapacity) free during
    the specified timeslot. If overlap with Friday prayer => returns [].
    """
    # If overlapping prayer => no rooms
    if overlaps_friday_prayer(day_of_week, start_time_str, end_time_str):
        return []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query all active rooms
    cursor.execute("SELECT RoomID, Location, MaxRoomCapacity FROM Room WHERE ActiveFlag = 1")
    all_rooms = cursor.fetchall()
    all_room_ids = [r['RoomID'] for r in all_rooms]

    # Find rooms booked in overlapping times
    sql_booked = """
        SELECT DISTINCT RoomID
        FROM SessionSchedule
        WHERE DayOfWeek = %s
          AND StartTime < %s
          AND EndTime > %s
    """
    cursor.execute(sql_booked, (day_of_week, end_time_str, start_time_str))
    booked_rooms = cursor.fetchall()
    booked_room_ids = [br['RoomID'] for br in booked_rooms]

    # Subtract => free rooms
    free_room_ids = list(set(all_room_ids) - set(booked_room_ids))
    if not free_room_ids:
        cursor.close()
        conn.close()
        return []

    placeholders = ','.join(['%s'] * len(free_room_ids))
    sql_free = f"SELECT RoomID, Location, MaxRoomCapacity FROM Room WHERE RoomID IN ({placeholders})"
    cursor.execute(sql_free, tuple(free_room_ids))
    free_rooms = cursor.fetchall()

    cursor.close()
    conn.close()
    return free_rooms

# ----------------------------------------------------
# Check Lecturer Availability (with Friday constraint)
# ----------------------------------------------------
def lecturer_is_free(lecturer_name, day_of_week, start_time_str, end_time_str):
    """
    Returns False if the lecturer is busy or if timeslot overlaps Friday prayer.
    """
    if overlaps_friday_prayer(day_of_week, start_time_str, end_time_str):
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT ss.*
        FROM SessionSchedule ss
        JOIN SessionAssignments sa ON ss.SessionID = sa.SessionID
        WHERE sa.LecturerName = %s
          AND ss.DayOfWeek = %s
          AND ss.StartTime < %s
          AND ss.EndTime > %s
    """
    cursor.execute(sql, (lecturer_name, day_of_week, end_time_str, start_time_str))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # If we found any rows => overlap => not free
    return (len(rows) == 0)

# ----------------------------------------------------
# Query: Fetch joined data for Timetable
# ----------------------------------------------------
def fetch_sessions_join_schedule():
    """
    Pulls data from SessionAssignments + SessionSchedule => combined schedule.
    Converts TIME columns to "HH:MM" for StartTime/EndTime.
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

    # Convert TIME fields from timedelta -> "HH:MM"
    for r in rows:
        start_td = r["StartTime"]
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

    # GET all lecturers
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

    # GET: show all rooms
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

        # Map CourseID -> CourseCode
        cursor.execute("SELECT CourseCode FROM Course WHERE CourseID=%s AND ActiveFlag=1", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            flash("Invalid or inactive course.")
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

            # Validate
            if not all([cohort_name, lecturer_main, session_type, duration_str]):
                flash(f"Missing data in session row {i+1}.")
                continue
            if not is_valid_duration(duration_str):
                flash(f"Invalid duration format: {duration_str}.")
                continue
            try:
                enrollments = int(enrollments)
            except ValueError:
                enrollments = 0

            # Choose lecturer
            if session_type.lower() == 'discussion' and lecturer_intern:
                chosen_lecturer = lecturer_intern
            else:
                chosen_lecturer = lecturer_main

            # Insert to DB
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

        flash("Sessions saved for selected course!")
        return redirect(url_for('assign_sessions'))

    # GET
    cursor.execute("SELECT CourseID, CourseCode, CourseName, Credits FROM Course WHERE ActiveFlag=1")
    courses_data = cursor.fetchall()

    cursor.execute("SELECT LecturerName FROM Lecturer WHERE ActiveFlag=1")
    lecturers_data = cursor.fetchall()

    cursor.execute("SELECT DISTINCT SessionType FROM SessionAssignments")
    session_types_raw = cursor.fetchall()
    session_types_data = [row[0] for row in session_types_raw] if session_types_raw else ['Lecture','Discussion']

    cursor.execute("SELECT DISTINCT Duration FROM SessionAssignments")
    durations_raw = cursor.fetchall()
    durations_data = [str(row[0]) for row in durations_raw] if durations_raw else ['01:00:00','01:30:00']

    cursor.close()
    conn.close()

    return render_template('assign_sessions.html',
                           courses=courses_data,
                           lecturers=lecturers_data,
                           session_types=session_types_data,
                           durations=durations_data)

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
    """
    Renders the Feasibility Check page, displaying detailed conflict information
    for student groups based on their scheduling.
    """
    # Run the feasibility check to get conflict details
    conflicts = run_feasibility_check()

    # Render the 'feasibility.html' template with the conflicts data
    return render_template('feasibility.html', conflicts=conflicts)

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

        # Validate input
        if not student_id:
            flash("No student selected.", "danger")
            return redirect(url_for('student_courses'))

        # Update the StudentCourseSelection table
        try:
            cursor.execute("DELETE FROM StudentCourseSelection WHERE StudentID=%s", (student_id,))
            insert_sql = """
                INSERT INTO StudentCourseSelection (StudentID, CourseCode)
                VALUES (%s, %s)
            """
            for ccode in selected_codes:
                cursor.execute(insert_sql, (student_id, ccode))
            conn.commit()
            flash("Courses updated successfully!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error updating courses: {err}", "danger")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('student_courses'))

    # GET request handling
    # Fetch students with their MajorName by joining the Major table
    cursor.execute("""
        SELECT s.StudentID, s.MajorID, s.YearNumber, m.MajorName
        FROM Student s
        JOIN Major m ON s.MajorID = m.MajorID
        ORDER BY m.MajorName, s.YearNumber, s.StudentID
    """)
    students_data = cursor.fetchall()

    # Fetch active courses
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
    sessions = fetch_sessions_join_schedule()
    return render_template('timetable.html', sessions=sessions)

# ----------------------------------------------------
# Check Conflict (Drag-and-Drop)
# ----------------------------------------------------
@app.route('/check_conflict', methods=['POST'])
def check_conflict():
    """
    Here is where you'd do advanced overlap checks if needed.
    For now, returns conflict=False.
    """
    data = request.json
    session_id = data.get("SessionID")
    new_day = data.get("NewDay")
    new_start = data.get("NewStartTime")

    # Could check same lecturer / cohort overlap in DB
    conflict_found = False
    reason = ""

    return jsonify({"conflict": conflict_found, "reason": reason})

# ----------------------------------------------------
# Save Timetable (Drag-and-Drop)
# ----------------------------------------------------
@app.route('/save_timetable', methods=['POST'])
def save_timetable():
    data = request.json  # list of {SessionID, DayOfWeek, StartTime, EndTime}
    conn = get_db_connection()
    cursor = conn.cursor()

    for sess in data:
        sid  = sess["SessionID"]
        day  = sess["DayOfWeek"]
        st   = sess["StartTime"]
        en   = sess["EndTime"]
        sql  = """
          UPDATE SessionSchedule
          SET DayOfWeek=%s, StartTime=%s, EndTime=%s
          WHERE SessionID=%s
        """
        cursor.execute(sql, (day, st, en, sid))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Timetable saved successfully"})

# ----------------------------------------------------
# Route: Conflicts -> show UnassignedSessions
# ----------------------------------------------------
@app.route('/conflicts', methods=['GET'])
def conflicts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM UnassignedSessions")
    unassigned = cursor.fetchall()

    cursor.execute("SELECT RoomID, Location, MaxRoomCapacity FROM Room WHERE ActiveFlag=1")
    rooms = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('conflict_resolution.html', unassigned=unassigned, rooms=rooms)

# ----------------------------------------------------
# Route: Suggest Alternatives
#  (incorporates day-limit + Friday prayer constraints)
# ----------------------------------------------------
@app.route('/suggest_alternatives', methods=['POST'])
def suggest_alternatives():
    """
    1) If lecturer has fewer than 3 distinct days => Monday–Friday.
    2) If 3+ => only assigned days.
    3) Skip Fri 11:50–12:15.
    4) Check capacity & lecturer free => yield as alternative.
    """
    data = request.json
    session_id  = data.get("SessionID")
    enrollments = data.get("NumberOfEnrollments", 0)
    lecturer    = data.get("LecturerName")

    # A: which days is this lecturer assigned?
    assigned = lecturer_assigned_days(lecturer)
    if len(assigned) < 3:
        possible_days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    else:
        possible_days = sorted(list(assigned))

    # B: example timeslots
    possible_times = [
        ("08:00","09:00"),("09:00","10:00"),("10:00","11:00"),
        ("11:00","12:00"),("12:00","13:00"),("13:00","14:00"),
        ("14:00","15:00"),("15:00","16:00")
    ]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT RoomID, Location, MaxRoomCapacity FROM Room WHERE ActiveFlag=1")
    all_rooms = cursor.fetchall()
    cursor.close()
    conn.close()

    free_slots = []
    for day in possible_days:
        for (st, en) in possible_times:
            # skip if Fri overlap
            if overlaps_friday_prayer(day, st, en):
                continue

            for r in all_rooms:
                if r['MaxRoomCapacity'] >= enrollments:
                    # check if room is free
                    rr = rooms_free_for_timeslot(day, st, en)
                    # check if lecturer free
                    lf = lecturer_is_free(lecturer, day, st, en)
                    room_ids = [x['RoomID'] for x in rr]

                    if r['RoomID'] in room_ids and lf:
                        free_slots.append({
                            "Day": day,
                            "StartTime": st,
                            "EndTime": en,
                            "RoomID": r['RoomID'],
                            "Location": r['Location']
                        })

    return jsonify({"alternatives": free_slots})

# ----------------------------------------------------
# Route: Resolve Conflict -> move from UnassignedSessions -> SessionSchedule
# ----------------------------------------------------
@app.route('/resolve_conflict', methods=['POST'])
def resolve_conflict():
    data = request.json
    session_id  = data["SessionID"]
    day_of_week = data["DayOfWeek"]
    start_time  = data["StartTime"]
    end_time    = data["EndTime"]
    room_id     = data["RoomID"]

    # check if Fri prayer overlap
    if overlaps_friday_prayer(day_of_week, start_time, end_time):
        return jsonify({"message": "Cannot schedule during Friday prayer time!"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # remove from UnassignedSessions
    cursor.execute("DELETE FROM UnassignedSessions WHERE SessionID=%s", (session_id,))

    # Insert or update SessionSchedule
    #  If you do an insert, you might do:
    insert_sql = """
      INSERT INTO SessionSchedule (SessionID, DayOfWeek, StartTime, EndTime, RoomID)
      VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (session_id, day_of_week, start_time, end_time, room_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Session assigned successfully!"})

# ----------------------------------------------------
# Main
# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)