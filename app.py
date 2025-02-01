#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import re
import threading
import os
import logging
import json
from datetime import datetime, timedelta, time
from collections import defaultdict
import random

# Local module imports
from scheduling.scheduler import schedule_sessions as run_schedule
from scheduling.feasibility_checker import run_feasibility_check

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with a secure secret key

# ----------------------------------------------------
# Configure Logging
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s %(levelname)s:%(message)s'
)

# ----------------------------------------------------
# MySQL Database Connection
# ----------------------------------------------------
def get_db_connection():
    """
    Connects to your schedulai database using mysql.connector.
    Adjust host/user/password if needed.
    """
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Naakey057@',
            database='schedulai'
        )
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection failed: {err}")
        return None

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
# Utility: Convert time objects -> "HH:MM"
# ----------------------------------------------------
def convert_time_to_hhmm(time_obj):
    """
    Converts a datetime.time or datetime.timedelta object to "HH:MM" string.
    """
    if isinstance(time_obj, timedelta):
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    elif isinstance(time_obj, time):
        return time_obj.strftime("%H:%M")
    else:
        return "00:00"

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
    if conn is None:
        logging.error("Failed to connect to the database in lecturer_assigned_days.")
        return set()
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql = """
                SELECT DISTINCT ss.DayOfWeek AS day
                FROM SessionSchedule ss
                JOIN SessionAssignments sa ON ss.SessionID = sa.SessionID
                WHERE sa.LecturerName = %s
            """
            cursor.execute(sql, (lecturer_name,))
            rows = cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error fetching lecturer assigned days: {err}")
        rows = []
    finally:
        conn.close()

    return {row['day'] for row in rows}

# ----------------------------------------------------
# Check Room Availability (with Friday constraint)
# ----------------------------------------------------
def rooms_free_for_timeslot(day_of_week, start_time_str, end_time_str):
    """
    Returns a list of dicts with keys:
      - Location
      - RoomName
      - MaxRoomCapacity
    that are free during the specified timeslot.
    If overlap with Friday prayer => returns [].
    """
    # If overlapping prayer => no rooms
    if overlaps_friday_prayer(day_of_week, start_time_str, end_time_str):
        return []

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in rooms_free_for_timeslot.")
        return []

    try:
        with conn.cursor(dictionary=True) as cursor:
            # Query all active rooms
            cursor.execute("SELECT Location, Location AS RoomName, MaxRoomCapacity FROM Room WHERE ActiveFlag = 1")
            all_rooms = cursor.fetchall()
            all_room_names = [r['RoomName'] for r in all_rooms]

            # Find rooms booked in overlapping times
            sql_booked = """
                SELECT DISTINCT RoomName
                FROM SessionSchedule
                WHERE DayOfWeek = %s
                  AND StartTime < %s
                  AND EndTime > %s
            """
            cursor.execute(sql_booked, (day_of_week, end_time_str, start_time_str))
            booked_rooms = cursor.fetchall()
            booked_room_names = [br['RoomName'] for br in booked_rooms]

            # Subtract => free rooms
            free_room_names = list(set(all_room_names) - set(booked_room_names))
            if not free_room_names:
                return []

            placeholders = ','.join(['%s'] * len(free_room_names))
            sql_free = f"SELECT Location AS RoomName, Location, MaxRoomCapacity FROM Room WHERE Location IN ({placeholders})"
            cursor.execute(sql_free, tuple(free_room_names))
            free_rooms = cursor.fetchall()

        return free_rooms

    except mysql.connector.Error as err:
        logging.error(f"Error checking room availability: {err}")
        return []
    finally:
        conn.close()

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
    if conn is None:
        logging.error("Failed to connect to the database in lecturer_is_free.")
        return False

    try:
        with conn.cursor(dictionary=True) as cursor:
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
    except mysql.connector.Error as err:
        logging.error(f"Error checking lecturer availability: {err}")
        rows = []
    finally:
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
    if conn is None:
        logging.error("Failed to connect to the database in fetch_sessions_join_schedule.")
        return []
    
    try:
        with conn.cursor(dictionary=True) as cursor:
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
    except mysql.connector.Error as err:
        logging.error(f"Error fetching sessions and schedule: {err}")
        rows = []
    finally:
        conn.close()

    # Convert TIME fields from time or timedelta to "HH:MM"
    for r in rows:
        start_time = r["StartTime"]
        end_time   = r["EndTime"]
        r["StartTime"] = convert_time_to_hhmm(start_time)
        r["EndTime"]   = convert_time_to_hhmm(end_time)

    logging.info("Fetched sessions and schedule successfully.")
    return rows

# ----------------------------------------------------
# ROUTE 1: Lecturers
# ----------------------------------------------------
@app.route('/lecturers', methods=['GET', 'POST'])
def lecturers():
    logging.info("Accessed /lecturers route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor() as cursor:
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
                logging.info(f"Updated active lecturers: {selected_lecturers}")
    
                return redirect(url_for('rooms'))
    
            # GET all lecturers
            cursor.execute("SELECT LecturerID, LecturerName FROM Lecturer")
            lecturers_data = cursor.fetchall()
    
    except mysql.connector.Error as err:
        logging.error(f"Error in /lecturers route: {err}")
        flash("An error occurred while fetching lecturers.", "danger")
        lecturers_data = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('lecturers.html', lecturers=lecturers_data)

# ----------------------------------------------------
# ROUTE 2: Rooms
# ----------------------------------------------------
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    logging.info("Accessed /rooms route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                selected_rooms = request.form.getlist('room_ids')
                session['active_rooms'] = selected_rooms
    
                cursor.execute("UPDATE Room SET ActiveFlag = 0")
                if selected_rooms:
                    placeholders = ','.join(['%s'] * len(selected_rooms))
                    sql = f"UPDATE Room SET ActiveFlag = 1 WHERE Location IN ({placeholders})"
                    cursor.execute(sql, tuple(selected_rooms))
                conn.commit()
                logging.info(f"Updated active rooms: {selected_rooms}")
    
                return redirect(url_for('assign_sessions'))
    
            # GET: show all rooms
            cursor.execute("SELECT Location, Location AS RoomName, MaxRoomCapacity FROM Room")
            rooms_data = cursor.fetchall()
    
    except mysql.connector.Error as err:
        logging.error(f"Error in /rooms route: {err}")
        flash("An error occurred while fetching rooms.", "danger")
        rooms_data = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('rooms.html', rooms=rooms_data)

# ----------------------------------------------------
# ROUTE 3: Assign Sessions (Populate SessionAssignments)
# ----------------------------------------------------
@app.route('/assign_sessions', methods=['GET', 'POST'])
def assign_sessions():
    logging.info("Accessed /assign_sessions route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                session_count = request.form.get('session_count', '0')
                try:
                    session_count = int(session_count)
                except ValueError:
                    flash("Invalid session count.", "danger")
                    return redirect(url_for('assign_sessions'))
                
                course_id = request.form.get('current_course_id')
                if not course_id:
                    flash("No course selected.", "danger")
                    return redirect(url_for('assign_sessions'))
                
                # Map CourseID -> CourseCode
                cursor.execute("SELECT CourseCode FROM Course WHERE CourseID=%s AND ActiveFlag=1", (course_id,))
                course_row = cursor.fetchone()
                if not course_row:
                    flash("Invalid or inactive course.")
                    return redirect(url_for('assign_sessions'))
                course_code = course_row[0]
    
                for i in range(session_count):
                    cohort_name = request.form.get(f'cohort_name_{i}', '').strip()
                    lecturer_main = request.form.get(f'lecturer_main_name_{i}', '').strip()
                    lecturer_intern = request.form.get(f'lecturer_intern_name_{i}', '').strip()
                    session_type = request.form.get(f'session_type_{i}', '').strip()
                    duration_str = request.form.get(f'duration_{i}', '').strip()
                    enrollments = request.form.get(f'enrollments_{i}', '0').strip()
    
                    # Validate
                    if not all([cohort_name, lecturer_main, session_type, duration_str]):
                        flash(f"Missing data in session row {i+1}.", "warning")
                        continue
                    if not is_valid_duration(duration_str):
                        flash(f"Invalid duration format: {duration_str}.", "warning")
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
                flash("Sessions saved for selected course!", "success")
    
            # GET request handling
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
    
    except mysql.connector.Error as err:
        logging.error(f"Error in /assign_sessions route: {err}")
        flash("An error occurred while assigning sessions.", "danger")
        courses_data = []
        lecturers_data = []
        session_types_data = []
        durations_data = []
    finally:
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
    logging.info("Accessed /run_scheduler route.")
    if request.method == 'POST':
        session_csv = os.path.join(os.path.dirname(__file__), 'scheduling', 'Session_Location_Preferences.csv')
        try:
            scheduler_thread = threading.Thread(target=run_schedule, args=(session_csv,))
            scheduler_thread.start()
            flash("Scheduling started in the background.", "success")
            logging.info("Scheduler thread started.")
        except Exception as e:
            flash(f"Error scheduling: {e}", "danger")
            logging.error(f"Scheduler failed: {e}")
        return redirect(url_for('summary'))
    
    return render_template('run_scheduler.html')

# ----------------------------------------------------
# ROUTE 5: Summary Page
# ----------------------------------------------------
@app.route('/summary')
def summary():
    logging.info("Accessed /summary route.")
    conn = get_db_connection()
    if conn is None:
        flash("Failed DB connection.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor(dictionary=True) as cursor:
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
            cursor.execute(query)
            assignments = cursor.fetchall()
    
        # Convert TIME fields to "HH:MM" format
        for assignment in assignments:
            assignment["StartTime"] = convert_time_to_hhmm(assignment["StartTime"])
            assignment["EndTime"] = convert_time_to_hhmm(assignment["EndTime"])
    
    except mysql.connector.Error as err:
        logging.error(f"Error fetching summary: {err}")
        flash("An error occurred while fetching the summary.", "danger")
        assignments = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('summary.html', assignments=assignments)


# ----------------------------------------------------
# Route: Course Selection
# ----------------------------------------------------
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    logging.info("Accessed /courses route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                selected_course_codes = request.form.getlist('course_codes')
                session['selected_courses'] = selected_course_codes
                logging.info(f"Selected courses: {selected_course_codes}")
                return redirect(url_for('assign_sessions'))
    
            cursor.execute("""
                SELECT CourseCode, CourseName, Credits
                FROM Course
                WHERE ActiveFlag = 1
                ORDER BY CourseCode
            """)
            courses_data = cursor.fetchall()
    
    except mysql.connector.Error as err:
        logging.error(f"Error in /courses route: {err}")
        flash("An error occurred while fetching courses.", "danger")
        courses_data = []
    finally:
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
    logging.info("Accessed /feasibility route.")
    try:
        # Run the feasibility check to get conflict details
        conflicts = run_feasibility_check()
        logging.info(f"Feasibility check completed with {len(conflicts)} conflicts.")
    except Exception as e:
        logging.error(f"Error during feasibility check: {e}")
        flash("An error occurred during the feasibility check.", "danger")
        conflicts = []
    
    # Render the 'feasibility.html' template with the conflicts data
    return render_template('feasibility.html', conflicts=conflicts)

# ----------------------------------------------------
# Route: Student->Courses bridging
# ----------------------------------------------------
@app.route('/student_courses', methods=['GET', 'POST'])
def student_courses():
    logging.info("Accessed /student_courses route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            
            if request.method == 'POST':
                student_id = request.form.get('student_id')
                
                # 1) Gather the "recommended" courses that were checked
                selected_courses = request.form.getlist('course_codes')
                
                # 2) Gather any "additional" courses from the multiple-select boxes under each Type
                #    They come in as a list of 'CourseCode|Type' strings.
                additional_courses = request.form.getlist('additional_course_codes')
                
                # 3) Combine them (avoid duplicates if desired)
                all_chosen_courses = selected_courses + additional_courses
                
                # 4) Validate input
                if not student_id:
                    flash("No student selected.", "danger")
                    return redirect(url_for('student_courses'))
                
                # Define allowed Type values based on your ENUM in the database
                allowed_types = [
                    'No Subtype', 
                    'Type I', 'Type II', 'Type III', 'Type IV', 'Type V', 
                    'Type VI', 'Type VII', 'Type VIII', 'Type IX', 'Type X'
                ]
                
                # 5) Update the StudentCourseSelection table
                try:
                    # Remove existing selections for the student
                    cursor.execute("DELETE FROM StudentCourseSelection WHERE StudentID = %s", (student_id,))
                    
                    insert_sql = """
                        INSERT INTO StudentCourseSelection (StudentID, CourseCode, Type)
                        VALUES (%s, %s, %s)
                    """
                    
                    for course_entry in all_chosen_courses:
                        try:
                            # Split the course entry to get CourseCode and Type
                            # Expected format: "CourseCode|Type"
                            course_code, course_type = course_entry.split('|')
                        except ValueError:
                            # If Type is not provided or format is incorrect, default to 'No Subtype'
                            course_code = course_entry.strip()
                            course_type = 'No Subtype'
                            logging.warning(f"Type not specified for course {course_code}. Defaulting to 'No Subtype'.")
                        
                        # Trim any whitespace
                        course_code = course_code.strip()
                        course_type = course_type.strip()
                        
                        # Validate the Type
                        if course_type not in allowed_types:
                            flash(f"Invalid type '{course_type}' for course '{course_code}'.", "danger")
                            logging.error(f"Invalid type '{course_type}' for course '{course_code}'. Skipping insertion.")
                            continue  # Skip invalid entries
                        
                        # Optionally, validate that the CourseCode exists in the Course table
                        cursor.execute("SELECT COUNT(*) AS count FROM Course WHERE CourseCode = %s", (course_code,))
                        course_exists = cursor.fetchone()['count'] > 0
                        if not course_exists:
                            flash(f"Course code '{course_code}' does not exist.", "danger")
                            logging.error(f"Course code '{course_code}' does not exist. Skipping insertion.")
                            continue  # Skip non-existent courses
                        
                        # Insert into the database
                        cursor.execute(insert_sql, (student_id, course_code, course_type))
                    
                    # Commit the transaction after all insertions
                    conn.commit()
                    
                    flash("Courses updated successfully!", "success")
                    logging.info(f"Updated courses for student {student_id}: {all_chosen_courses}")
                
                except mysql.connector.Error as err:
                    # Rollback the transaction in case of any database errors
                    conn.rollback()
                    logging.error(f"Error updating courses for student {student_id}: {err}")
                    flash(f"Error updating courses: {err}", "danger")
        
            # --- GET Request Handling ---
            # 1) Students with their Major
            cursor.execute("""
                SELECT s.StudentID, s.MajorID, s.YearNumber, m.MajorName
                FROM Student s
                JOIN Major m ON s.MajorID = m.MajorID
                ORDER BY m.MajorName, s.YearNumber, s.StudentID
            """)
            students_data = cursor.fetchall()
            
            # 2) All active courses (to display in "Add More" dropdowns)
            cursor.execute("""
                SELECT CourseCode, CourseName
                FROM Course
                WHERE ActiveFlag = 1
                ORDER BY CourseCode
            """)
            all_active_courses = cursor.fetchall()
    
    except mysql.connector.Error as err:
        logging.error(f"Error in /student_courses route: {err}")
        flash("An error occurred while fetching student courses.", "danger")
        students_data = []
        all_active_courses = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        'student_courses.html',
        students=students_data,
        all_courses=all_active_courses
    )



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
    
    # Implement actual conflict checking logic here if needed
    conflict_found = False
    reason = ""
    
    return jsonify({"conflict": conflict_found, "reason": reason})

# ----------------------------------------------------
# Save Timetable (Drag-and-Drop)
# ----------------------------------------------------
@app.route('/save_timetable', methods=['POST'])
def save_timetable():
    data = request.json  # list of {SessionID, DayOfWeek, StartTime, EndTime, Location}
    logging.info("Accessed /save_timetable route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return jsonify({"message": "Database connection failed."}), 500
    
    try:
        with conn.cursor() as cursor:
            for sess in data:
                sid  = sess["SessionID"]
                day  = sess["DayOfWeek"]
                st   = sess["StartTime"]
                en   = sess["EndTime"]
                location = sess["Location"]
                sql  = """
                  UPDATE SessionSchedule
                  SET DayOfWeek=%s, StartTime=%s, EndTime=%s, RoomName=%s
                  WHERE SessionID=%s
                """
                cursor.execute(sql, (day, st, en, location, sid))
            conn.commit()
            logging.info(f"Saved timetable for {len(data)} sessions.")
        return jsonify({"message": "Timetable saved successfully"}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Error saving timetable: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# ----------------------------------------------------
# Route: Conflicts -> show UnassignedSessions
# ----------------------------------------------------
@app.route('/conflicts', methods=['GET'])
def conflicts():
    logging.info("Accessed /conflicts route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM UnassignedSessions")
            unassigned = cursor.fetchall()
    
            cursor.execute("SELECT Location, Location AS RoomName, MaxRoomCapacity FROM Room WHERE ActiveFlag=1")
            rooms = cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error fetching conflicts: {err}")
        flash("An error occurred while fetching conflicts.", "danger")
        unassigned = []
        rooms = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('conflict_resolution.html', unassigned=unassigned, rooms=rooms)

# ----------------------------------------------------
# Route: Suggest Alternatives
#  (incorporates exclusion of existing scheduled days, Friday prayer constraints, and matches session duration)
# ----------------------------------------------------
@app.route('/suggest_alternatives', methods=['POST'])
def suggest_alternatives():
    """
    Suggests alternative time slots based on lecturer availability, room capacity, session duration,
    excluding days already in the lecturer's existing schedule, and considering Friday prayer constraints.
    """
    data = request.json
    session_id  = data.get("SessionID")
    enrollments = data.get("NumberOfEnrollments", 0)
    lecturer    = data.get("LecturerName")
    
    logging.info(f"Suggesting alternatives for SessionID: {session_id}, Lecturer: {lecturer}, Enrollments: {enrollments}")
    
    if not session_id or not lecturer:
        logging.warning("Invalid data received in /suggest_alternatives route.")
        return jsonify({"message": "Invalid data. 'SessionID' and 'LecturerName' are required."}), 400
    
    # A: Fetch session's duration from the database
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in suggest_alternatives.")
        return jsonify({"message": "Database connection failed."}), 500
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT Duration
                FROM SessionAssignments
                WHERE SessionID = %s
            """, (session_id,))
            row = cursor.fetchone()

            if not row or not row['Duration']:
                logging.warning(f"Session duration not found for SessionID: {session_id}")
                return jsonify({"message": "Session duration not found."}), 400

            duration_obj = row['Duration']
            session_duration = 0  # Initialize

            if isinstance(duration_obj, timedelta):
                total_seconds = int(duration_obj.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                session_duration = hours * 60 + minutes + (1 if seconds >= 30 else 0)  # Round up if seconds >= 30
                logging.debug(f"Duration (timedelta) for SessionID {session_id}: {hours}h {minutes}m {seconds}s")
            elif isinstance(duration_obj, str):
                try:
                    h, m, s = map(int, duration_obj.split(':'))
                    session_duration = h * 60 + m + (1 if s >= 30 else 0)
                    logging.debug(f"Duration (str) for SessionID {session_id}: {h}h {m}m {s}s")
                except:
                    logging.error(f"Invalid session duration format for SessionID: {session_id}")
                    return jsonify({"message": "Invalid session duration format."}), 400
            else:
                logging.error(f"Unsupported duration type for SessionID: {session_id}")
                return jsonify({"message": "Invalid session duration format."}), 400

            # B: Determine possible days based on lecturer's current assignments
            assigned_days = lecturer_assigned_days(lecturer)
            all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            # Exclude days already assigned to the lecturer
            possible_days = [day for day in all_days if day not in assigned_days]

            logging.debug(f"Assigned days for lecturer {lecturer}: {assigned_days}")
            logging.debug(f"Possible alternative days: {possible_days}")

            # C: Define possible timeslots (HH:MM format)
            possible_times = [
                # Define timeslots as needed, possibly generated dynamically
                ("08:00","09:30"),("08:00","09:00"),("08:00","10:00"),
                ("08:00","10:30"),("08:30","11:00"),("08:30","09:30"),
                ("08:30","10:30"),("08:30","10:00"),("08:40","10:40"),
                ("08:40","09:40"),("08:40","11:10"),("08:40","10:10"),
                ("08:50","09:50"),("08:50","10:20"),("08:50","11:20"),
                ("08:50","10:50"),("09:10","11:10"),("09:10","11:40"),
                ("09:10","10:10"),("09:10","10:40"),("09:45","11:15"),
                ("09:45","10:45"),("09:45","12:15"),("09:45","11:45"),
                ("09:50","11:50"),("09:50","10:50"),("09:50","12:20"),
                ("09:50","11:20"),("10:10","11:10"),("10:10","11:40"),
                ("10:10","12:40"),("10:10","12:10"),("10:20","12:20"),
                ("10:20","11:50"),("10:20","11:20"),("10:20","12:50"),
                ("10:30","12:30"),("10:30","12:00"),("10:30","13:00"),
                ("10:30","11:30"),("11:00","12:30"),("11:00","12:00"),
                ("11:00","13:00"),("11:00","13:30"),("11:30","12:30"),
                ("11:30","13:00"),("11:30","14:00"),("11:30","13:30"),
                ("12:00","14:00"),("12:00","13:30"),("12:00","13:00"),
                ("12:00","14:30"),("12:15","13:15"),("12:15","14:15"),
                ("12:15","14:45"),("12:15","13:45"),("12:30","14:00"),
                ("12:30","13:30"),("12:30","14:30"),("12:30","15:00"),
                ("12:45","14:45"),("12:45","15:15"),("12:45","13:45"),
                ("12:45","14:15"),("13:15","14:15"),("13:15","15:15"),
                ("13:15","14:45"),("13:15","15:45"),("13:45","16:15"),
                ("13:45","15:15"),("13:45","14:45"),("13:45","15:45"),
                ("13:50","16:20"),("13:50","15:50"),("13:50","14:50"),
                ("13:50","15:20"),("13:55","16:25"),("13:55","15:25"),
                ("13:55","14:55"),("13:55","15:55"),("14:25","16:55"),
                ("14:25","15:55"),("14:25","16:25"),("14:25","15:25"),
                ("14:40","15:40"),("14:40","16:40"),("14:40","17:10"),
                ("14:40","16:10"),("14:45","16:15"),("14:45","16:45"),
                ("14:45","15:45"),("14:45","17:15"),("15:00","16:30"),
                ("15:00","16:00"),("15:00","17:30"),("15:00","17:00"),
                ("15:30","18:00"),("15:30","16:30"),("15:30","17:30"),
                ("15:30","17:00"),("16:00","18:00"),("16:00","17:30"),
                ("16:00","18:30"),("16:00","17:00"),("16:10","17:10"),
                ("16:10","18:40"),("16:10","17:40"),("16:10","18:10"),
                ("16:40","18:10"),("16:40","18:40"),("16:40","17:40"),
                ("16:45","17:45")
            ]
    
            # D: Fetch all active rooms that can accommodate the enrollments
            cursor.execute("""
                SELECT Location, Location AS RoomName, MaxRoomCapacity 
                FROM Room 
                WHERE ActiveFlag = 1 AND MaxRoomCapacity >= %s
            """, (enrollments,))
            suitable_rooms = cursor.fetchall()
    
        # No suitable rooms found
        if not suitable_rooms:
            logging.info("No suitable rooms found for the given enrollments.")
            return jsonify({"alternatives": []})
    
    except mysql.connector.Error as err:
        logging.error(f"Error fetching session duration or rooms: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        conn.close()
    
    free_slots = []
    for day in possible_days:
        for (st, en) in possible_times:
            # Calculate the duration of the timeslot
            try:
                start_hours, start_minutes = map(int, st.split(':'))
                end_hours, end_minutes = map(int, en.split(':'))
            except ValueError:
                logging.error(f"Invalid timeslot format: {st} - {en}")
                continue
            timeslot_duration = (end_hours * 60 + end_minutes) - (start_hours * 60 + start_minutes)
    
            # Only consider timeslots that match the session's duration
            if timeslot_duration != session_duration:
                continue
    
            # Skip timeslots that overlap with Friday prayer
            if overlaps_friday_prayer(day, st, en):
                continue
    
            for room in suitable_rooms:
                # Check if the room is free during the timeslot
                free_rooms = rooms_free_for_timeslot(day, st, en)
                if not any(r['RoomName'] == room['RoomName'] for r in free_rooms):
                    continue
    
                # Check if the lecturer is free during the timeslot
                if not lecturer_is_free(lecturer, day, st, en):
                    continue
    
                # If all conditions are met, add the slot to free_slots
                free_slots.append({
                    "Day": day,
                    "StartTime": st,
                    "EndTime": en,
                    "Location": room['Location'],
                    "MaxRoomCapacity": room['MaxRoomCapacity']
                })
    
    logging.info(f"Found {len(free_slots)} alternative slots for SessionID: {session_id}")
    return jsonify({"alternatives": free_slots})

# ----------------------------------------------------
# Route: Resolve Conflict -> move from UnassignedSessions -> SessionSchedule
# ----------------------------------------------------
@app.route('/resolve_conflict', methods=['POST'])
def resolve_conflict():
    """
    Assigns an unassigned session to a specific timeslot and room.
    Expects JSON data with 'SessionID', 'DayOfWeek', 'StartTime', 'EndTime', 'Location'.
    """
    logging.info("Accessed /resolve_conflict route.")
    data = request.json
    session_id  = data.get("SessionID")
    day_of_week = data.get("DayOfWeek")
    start_time  = data.get("StartTime")
    end_time    = data.get("EndTime")
    location    = data.get("Location")
    
    # Validate input
    if not all([session_id, day_of_week, start_time, end_time, location]):
        logging.warning("Incomplete data received in /resolve_conflict route.")
        return jsonify({"message": "Missing data. All fields are required."}), 400
    
    # Check if Friday prayer overlaps
    if overlaps_friday_prayer(day_of_week, start_time, end_time):
        logging.warning("Attempted to schedule during Friday prayer time.")
        return jsonify({"message": "Cannot schedule during Friday prayer time!"}), 400
    
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in resolve_conflict.")
        return jsonify({"message": "Database connection failed."}), 500
    
    try:
        with conn.cursor() as cursor:
            # Check if room is available
            sql_room = """
                SELECT COUNT(*) FROM SessionSchedule
                WHERE DayOfWeek = %s
                  AND RoomName = %s
                  AND StartTime < %s
                  AND EndTime > %s
            """
            cursor.execute(sql_room, (day_of_week, location, end_time, start_time))
            room_conflict = cursor.fetchone()[0] > 0
    
            if room_conflict:
                logging.info(f"Room {location} is already booked for the selected time slot.")
                return jsonify({"message": "Room is already booked for the selected time slot."}), 400
    
            # Check if lecturer is available
            cursor.execute("SELECT LecturerName FROM SessionAssignments WHERE SessionID=%s", (session_id,))
            lecturer_row = cursor.fetchone()
            if not lecturer_row:
                logging.warning(f"Lecturer not found for SessionID: {session_id}")
                return jsonify({"message": "Lecturer not found for the session."}), 404
            lecturer_name = lecturer_row[0]
    
            cursor.execute("""
                SELECT COUNT(*) FROM SessionSchedule ss
                JOIN SessionAssignments sa ON ss.SessionID = sa.SessionID
                WHERE sa.LecturerName = %s
                  AND ss.DayOfWeek = %s
                  AND ss.StartTime < %s
                  AND ss.EndTime > %s
            """, (lecturer_name, day_of_week, end_time, start_time))
            lecturer_conflict = cursor.fetchone()[0] > 0
    
            if lecturer_conflict:
                logging.info(f"Lecturer {lecturer_name} is already booked for the selected time slot.")
                return jsonify({"message": "Lecturer is already booked for the selected time slot."}), 400
    
            # Remove from UnassignedSessions
            cursor.execute("DELETE FROM UnassignedSessions WHERE SessionID=%s", (session_id,))
    
            # Insert into SessionSchedule
            insert_sql = """
                INSERT INTO SessionSchedule (SessionID, DayOfWeek, StartTime, EndTime, RoomName)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (session_id, day_of_week, start_time, end_time, location))
    
            conn.commit()
            logging.info(f"Session {session_id} assigned to {location} on {day_of_week} from {start_time} to {end_time}.")
    
        return jsonify({"message": "Session assigned successfully!"}), 200
    
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Database error during conflict resolution: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    
    finally:
        cursor.close()
        conn.close()

# ----------------------------------------------------
# Route: Get Existing Schedule for Cohort and Course
# ----------------------------------------------------
@app.route('/get_existing_schedule', methods=['POST'])
def get_existing_schedule():
    """
    Fetches the existing schedule (days, rooms, session types, and lecturers) for a given course code and cohort name.
    Expects JSON data with 'CourseCode' and 'CohortName'.
    Returns JSON with 'existing_schedule'.
    """
    logging.info("Accessed /get_existing_schedule route.")
    data = request.json
    course_code = data.get('CourseCode')
    cohort_name = data.get('CohortName')
    
    if not course_code or not cohort_name:
        logging.warning("Invalid data received in /get_existing_schedule route.")
        return jsonify({"message": "Invalid data. 'CourseCode' and 'CohortName' are required."}), 400
    
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in get_existing_schedule.")
        return jsonify({"message": "Database connection failed."}), 500
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Updated SQL Query to include SessionType and LecturerName
            sql = """
                SELECT sc.DayOfWeek, sc.StartTime, sc.EndTime, sc.RoomName, sa.SessionType, sa.LecturerName
                FROM SessionAssignments sa
                JOIN SessionSchedule sc ON sa.SessionID = sc.SessionID
                WHERE sa.CourseCode = %s AND sa.CohortName = %s
                ORDER BY sc.DayOfWeek, sc.StartTime
            """
            cursor.execute(sql, (course_code, cohort_name))
            rows = cursor.fetchall()
    
        # Convert TIME fields to "HH:MM" format
        for row in rows:
            row["StartTime"] = convert_time_to_hhmm(row["StartTime"])
            row["EndTime"] = convert_time_to_hhmm(row["EndTime"])
    
        logging.info(f"Fetched existing schedule for CourseCode: {course_code}, CohortName: {cohort_name}.")
        return jsonify({"existing_schedule": rows}), 200
    
    except mysql.connector.Error as err:
        logging.error(f"Error fetching existing schedule: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    
    finally:
        cursor.close()
        conn.close()

# ----------------------------------------------------
# Route: Edit Session
# ----------------------------------------------------
@app.route('/edit_session', methods=['POST'])
def edit_session():
    """
    Edits the details of an unassigned session.
    Expects JSON data with 'SessionID', 'CourseCode', 'CohortName', 'LecturerName', 'Duration', 'NumberOfEnrollments'.
    """
    logging.info("Accessed /edit_session route.")
    data = request.json
    session_id = data.get("SessionID")
    course_code = data.get("CourseCode")
    cohort_name = data.get("CohortName")
    lecturer_name = data.get("LecturerName")
    duration_str = data.get("Duration")  # Expected format: "HH:MM:SS"
    enrollments = data.get("NumberOfEnrollments")

    # Input Validation
    if not all([session_id, course_code, cohort_name, lecturer_name, duration_str, enrollments is not None]):
        logging.warning("Incomplete data received in /edit_session route.")
        return jsonify({"message": "Incomplete data. All fields are required."}), 400

    # Validate Duration Format
    pattern = r'^\d{1,2}:\d{2}:\d{2}$'
    if not re.match(pattern, duration_str):
        logging.warning(f"Invalid duration format received: {duration_str}")
        return jsonify({"message": "Invalid duration format. Expected 'HH:MM:SS'."}), 400

    # Validate Enrollments
    if not isinstance(enrollments, int) or enrollments < 0:
        logging.warning(f"Invalid number of enrollments received: {enrollments}")
        return jsonify({"message": "Number of enrollments must be a non-negative integer."}), 400

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in edit_session.")
        return jsonify({"message": "Database connection failed."}), 500

    try:
        with conn.cursor() as cursor:
            # Check if the session exists in UnassignedSessions
            cursor.execute("SELECT * FROM UnassignedSessions WHERE SessionID = %s", (session_id,))
            session_exists = cursor.fetchone()
            if not session_exists:
                logging.warning(f"SessionID {session_id} not found in UnassignedSessions.")
                return jsonify({"message": "Session not found."}), 404

            # Update the session details
            update_sql = """
                UPDATE UnassignedSessions
                SET CourseCode = %s,
                    CohortName = %s,
                    LecturerName = %s,
                    Duration = %s,
                    NumberOfEnrollments = %s
                WHERE SessionID = %s
            """
            cursor.execute(update_sql, (
                course_code,
                cohort_name,
                lecturer_name,
                duration_str,
                enrollments,
                session_id
            ))
            conn.commit()
            logging.info(f"Session {session_id} updated successfully.")

        return jsonify({"message": "Session updated successfully!"}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Database error during session edit: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        conn.close()
@app.route('/get_full_plan', methods=['GET'])
def get_full_plan():
    """
    Returns JSON for the full recommended plan for a given MajorID,
    grouping rows by YearNumber, SemesterNumber, SubType.
    Example row: { YearNumber, SemesterNumber, SubType, CourseCode, CourseName, Credits }
    """
    major_id = request.args.get('major_id', type=int)
    if not major_id:
        return jsonify({"plan": []}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"plan": []}), 500

    rows = []
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql = """
                SELECT
                  p.YearNumber,
                  p.SemesterNumber,
                  IFNULL(p.SubType, '') AS SubType,
                  c.CourseCode,
                  c.CourseName,
                  c.Credits
                FROM ProgramPlan p
                JOIN Course c ON p.CourseCode = c.CourseCode
                WHERE p.MajorID = %s
                ORDER BY p.YearNumber, p.SemesterNumber, p.SubType, c.CourseCode
            """
            cursor.execute(sql, (major_id,))
            rows = cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Database error in /get_full_plan: {err}")
    finally:
        conn.close()

    # Build JSON
    plan_data = []
    for r in rows:
        plan_data.append({
            "YearNumber": r["YearNumber"],
            "SemesterNumber": r["SemesterNumber"],
            "SubType": r["SubType"],  # '' or 'I','II','III'
            "CourseCode": r["CourseCode"],
            "CourseName": r["CourseName"],
            "Credits": float(r["Credits"])
        })
    return jsonify({"plan": plan_data}), 200

# ----------------------------------------------------
# ROUTE: Timetable Page
# ----------------------------------------------------
# ... [existing imports and configurations] ...

@app.route('/timetable', methods=['GET'])
def timetable():
    logging.info("Accessed /timetable route.")
    try:
        sessions = fetch_sessions_join_schedule()
        logging.info(f"Fetched {len(sessions)} sessions for timetable.")
        
        # Fetch all active rooms
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for('home'))
        
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT Location AS RoomName FROM Room WHERE ActiveFlag = 1 ORDER BY Location")
            rooms_data = cursor.fetchall()
            rooms = [room['RoomName'] for room in rooms_data]
        
        conn.close()
        
        # Group sessions by RoomName
        sessions_by_room = defaultdict(list)
        for sess in sessions:
            room = sess['RoomName']
            sessions_by_room[room].append(sess)
        
        # Define time slots (every 15 minutes from 08:00 to 19:00)
        time_slots = [
            '08:00', '08:15', '08:30', '08:45',
            '09:00', '09:15', '09:30', '09:45',
            '10:00', '10:15', '10:30', '10:45',
            '11:00', '11:15', '11:30', '11:45',
            '12:00', '12:15', '12:30', '12:45',
            '13:00', '13:15', '13:30', '13:45',
            '14:00', '14:15', '14:30', '14:45',
            '15:00', '15:15', '15:30', '15:45',
            '16:00', '16:15', '16:30', '16:45',
            '17:00', '17:15', '17:30', '17:45',
            '18:00', '18:15', '18:30', '18:45',
            '19:00'
        ]
        
        # Optionally, pass course_colors if needed (from your existing function)
        course_colors = generate_course_colors(sessions)
    
    except Exception as e:
        logging.error(f"Error fetching timetable data: {e}")
        flash("An error occurred while fetching the timetable.", "danger")
        sessions_by_room = {}
        rooms = []
        time_slots = []
        course_colors = {}
    
    return render_template(
        'timetable.html',
        rooms=rooms,
        sessions_by_room=sessions_by_room,
        time_slots=time_slots,
        course_colors=course_colors  # Pass this if you use dynamic course colors
    )

def generate_course_colors(sessions):
    course_colors = {}
    color_palette = [
        '#007bff', '#28a745', '#fd7e14', '#6f42c1', '#6c757d',
        '#17a2b8', '#ffc107', '#dc3545', '#20c997', '#6610f2'
    ]
    random.shuffle(color_palette)
    for session in sessions:
        course = session['CourseCode']
        if course not in course_colors:
            course_colors[course] = color_palette[len(course_colors) % len(color_palette)]
    return course_colors



def ordinal(n: int) -> str:
    """
    Converts an integer into its ordinal representation (e.g., 1 -> "1st").
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def convert_timedelta_to_hhmm(td):
    """
    Converts a timedelta object to "HH:MM" string.
    Returns "N/A" if td is None.
    """
    if not td:
        return "N/A"
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

# Mapping of MajorID to their Major Prefixes
major_prefix_mapping = {
    1: ['BUSA', 'ECON'],  # Business Administration
    2: ['CS'],            # Computer Science
    3: ['IS'],            # Management Information Systems
    4: ['CE', 'ENGR'],    # Computer Engineering
    5: ['MECH'],          # Mechatronics Engineering (Assumed prefix)
    6: ['ME', 'ENGR'],    # Mechanical Engineering
    7: ['EE', 'ENGR'],    # Electrical and Electronic Engineering
    8: ['LAW'],           # Law with Public Policy (Assumed prefix)
    # Add more mappings as necessary
}

# ----------------------------------------------------
# ROUTE: Home Page
# ----------------------------------------------------
@app.route('/')
def home():
    """
    Home page of the application.
    Lists all students with links to their timetables.
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        logging.error("Failed to connect to the database while accessing the home page.")
        return render_template('home.html', students=[])
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.StudentID, m.MajorName, s.YearNumber
                FROM Student s
                JOIN Major m ON s.MajorID = m.MajorID
                ORDER BY s.StudentID
            """)
            students = cursor.fetchall()
            logging.debug(f"Fetched {len(students)} students from the database.")
    except mysql.connector.Error as err:
        logging.error(f"Database query error while fetching students: {err}")
        flash('An error occurred while fetching student data.', 'danger')
        students = []
    finally:
        conn.close()
        logging.debug("Database connection closed after fetching students.")
    
    return render_template('home.html', students=students)

# ----------------------------------------------------
# ROUTE: Student Timetable with Electives
# ----------------------------------------------------
@app.route('/student_timetable/<int:student_id>/<string:day_of_week>', methods=['GET'])
def student_timetable(student_id, day_of_week):
    """
    Displays the timetable for a specific student based on StudentID and selected day.
    Shows all major and non-major electives that are active on this day, as well as
    regular (non-elective) sessions.
    """
    logging.info(f"Accessed /student_timetable route with StudentID={student_id}, Day={day_of_week}")
    
    # Validate day_of_week
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if day_of_week not in valid_days:
        logging.warning(f"Invalid day_of_week received: {day_of_week}")
        flash('Invalid day of week selected.', 'danger')
        return redirect(url_for('home'))
    
    # Establish database connection
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        logging.error(f"Failed to connect to the database for StudentID {student_id}.")
        return redirect(url_for('home'))
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            # --- (1) Fetch Student Information ---
            cursor.execute("""
                SELECT s.StudentID, s.MajorID, m.MajorName, s.YearNumber
                FROM Student s
                JOIN Major m ON s.MajorID = m.MajorID
                WHERE s.StudentID = %s
            """, (student_id,))
            student_info = cursor.fetchone()
            if not student_info:
                logging.warning(f"StudentID {student_id} not found.")
                flash('Student not found.', 'danger')
                return redirect(url_for('home'))
            
            major_id = student_info['MajorID']
            major_name = student_info['MajorName']
            year_number = student_info['YearNumber']
            
            student_label = f"StudentID {student_id}, {ordinal(year_number)}-year {major_name}"
            logging.debug(f"Student Label: {student_label}")
            
            # --- (2) Fetch Major Prefixes from Mapping ---
            major_prefixes = major_prefix_mapping.get(major_id, [])
            logging.debug(f"Major Prefixes for MajorID {major_id}: {major_prefixes}")
            if not major_prefixes:
                logging.warning(f"No major prefixes defined for MajorID {major_id} (StudentID {student_id}).")
                flash('No major prefixes defined for this student\'s major.', 'danger')
                return redirect(url_for('home'))

            # ---------------------------------------------------------------------
            # UPDATED SECTION: Fetch ALL Active Elective Courses for This Day
            # ---------------------------------------------------------------------
            # We'll retrieve any course whose RequirementType indicates 'Elective'
            # and that has an active session on the specified day_of_week.
            #
            # Then we'll classify them as Major or Non-Major by checking their code
            # against the student's major_prefixes.

            cursor.execute("""
                SELECT c.CourseCode, c.CourseName,
                    sa.LecturerName, sa.CohortName,    -- Added sa.CohortName here
                    ss.RoomName, ss.StartTime, ss.EndTime
                FROM Course c
                JOIN SessionAssignments sa ON c.CourseCode = sa.CourseCode
                JOIN SessionSchedule ss ON sa.SessionID = ss.SessionID
                WHERE c.RequirementType LIKE '%Elective%'
                AND c.ActiveFlag = 1
                AND ss.DayOfWeek = %s
                ORDER BY c.CourseCode, ss.StartTime
            """, (day_of_week,))
            all_elective_sessions = cursor.fetchall()
            logging.debug(f"Fetched {len(all_elective_sessions)} elective session(s) for day {day_of_week}.")

            # Separate them into Major vs. Non-Major based on prefix
            major_elective_details = []
            non_major_elective_details = []
            
            for row in all_elective_sessions:
                # Convert times to HH:MM
                row['Time'] = (
                    f"{convert_timedelta_to_hhmm(row['StartTime'])}"
                    f" - {convert_timedelta_to_hhmm(row['EndTime'])}"
                )

                # Check if CourseCode starts with any major prefix
                course_code = row['CourseCode']
                if any(course_code.startswith(prefix) for prefix in major_prefixes):
                    major_elective_details.append(row)
                else:
                    non_major_elective_details.append(row)

            logging.info(f"StudentID {student_id}, Day={day_of_week}: "
                         f"{len(major_elective_details)} major elective sessions, "
                         f"{len(non_major_elective_details)} non-major elective sessions.")

            # --- (8) Fetch Regular (Non-Elective) Sessions ---
            # (unchanged from your original code)
            cursor.execute("""
                SELECT sa.CourseCode,
                       sa.LecturerName,
                       sa.CohortName,
                       ss.StartTime,
                       ss.EndTime,
                       ss.RoomName
                FROM SessionAssignments sa
                JOIN SessionSchedule ss ON sa.SessionID = ss.SessionID
                JOIN Course c ON sa.CourseCode = c.CourseCode
                WHERE sa.CourseCode IN (
                    SELECT DISTINCT scc.CourseCode
                    FROM StudentCourseSelection scc
                    WHERE scc.StudentID = %s
                )
                  AND ss.DayOfWeek = %s
                  AND c.RequirementType NOT LIKE '%Elective%'
                  AND c.ActiveFlag = 1
                ORDER BY ss.StartTime
            """, (student_id, day_of_week))
            sessions = cursor.fetchall()
            logging.debug(f"Fetched {len(sessions)} regular (non-elective) sessions "
                          f"for StudentID {student_id} on {day_of_week}.")
            
            # Convert StartTime / EndTime to readable strings
            for session in sessions:
                session['Time'] = (
                    f"{convert_timedelta_to_hhmm(session['StartTime'])}"
                    f" - {convert_timedelta_to_hhmm(session['EndTime'])}"
                )
    
    except mysql.connector.Error as err:
        logging.error(f"Database query error: {err}")
        flash('An error occurred while fetching timetable data.', 'danger')
        sessions = []
        major_elective_details = []
        non_major_elective_details = []
    finally:
        conn.close()
        logging.debug(f"Database connection closed for StudentID {student_id}.")

    # Log warnings if no electives
    if not major_elective_details:
        logging.warning(f"No Major Electives found for StudentID {student_id} on {day_of_week}.")
    if not non_major_elective_details:
        logging.warning(f"No Non-Major Electives found for StudentID {student_id} on {day_of_week}.")
    
    # --- Render Timetable (unchanged) ---
    return render_template(
        'student_timetable.html',
        student_id=student_id,
        student_label=student_label,
        major_elective_details=major_elective_details,
        non_major_elective_details=non_major_elective_details,
        day_of_week=day_of_week,
        valid_days=valid_days,
        sessions=sessions
    )


# ----------------------------------------------------
# Main
# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)