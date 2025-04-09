#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
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
from sklearn.cluster import KMeans
import numpy as np
import pygad
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Template
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from flask_socketio import SocketIO, emit


# Local module imports
# Import the feasibility blueprint and function from the scheduling package.
from scheduling.feasibility_checker import feasibility_bp, generate_all_feasible_timetables_with_conflicts
from scheduling.scheduler import schedule_sessions as run_schedule
from scheduling.feasibility_checker import feasibility_bp, generate_all_feasible_timetables_with_conflicts, run_feasibility_check_background

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with a secure secret key

# Initialize SocketIO with the Flask app
socketio = SocketIO(app)

# Register the feasibility blueprint with an appropriate URL prefix.
# Here we register it at the root so that endpoints like /feasibility_check are available.
app.register_blueprint(feasibility_bp, url_prefix='/')
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

# ------------------------------
# Authentication Routes
# ------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username   = request.form.get('username')
        email      = request.form.get('email')
        password   = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        # For simplicity, assign a default role (e.g. RoleID=2 for a standard user)
        default_role_id = 2

        # Basic validation
        if not all([username, email, password, first_name, last_name]):
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to database and insert the new user
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username or email already exists
                sql_check = "SELECT * FROM Users WHERE Email = %s OR Username = %s"
                cursor.execute(sql_check, (email, username))
                if cursor.fetchone():
                    flash("Username or email already exists.", "warning")
                    return redirect(url_for('register'))

                # Insert the new user
                sql_insert = """
                    INSERT INTO Users (Username, Email, PasswordHash, FirstName, LastName, RoleID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (username, email, hashed_password, first_name, last_name, default_role_id))
                conn.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            conn.rollback()
            logging.error(f"Error registering user: {err}")
            flash("An error occurred during registration.", "danger")
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please provide both email and password.", "warning")
            return redirect(url_for('login'))

        conn = get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM Users WHERE Email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                if user and check_password_hash(user['PasswordHash'], password):
                    # Store necessary user details in the session
                    session['user'] = {
                        "UserID": user['UserID'],
                        "Username": user['Username'],
                        "Email": user['Email'],
                        "FirstName": user['FirstName'],
                        "LastName": user['LastName'],
                        "RoleID": user['RoleID']
                    }
                    flash("Login successful.", "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Invalid credentials. Please try again.", "danger")
                    return redirect(url_for('login'))
        except mysql.connector.Error as err:
            logging.error(f"Error during login: {err}")
            flash("An error occurred during login.", "danger")
        finally:
            conn.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

# ------------------------------
# Management Pages (Protected)
# ------------------------------

@app.route('/manage-rooms', methods=['GET', 'POST'])
def manage_rooms():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template('manage_rooms.html', rooms=[])
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            if request.method == 'POST':
                action = request.form.get('action')
                # ----------------
                # CREATE (Add New Room)
                # ----------------
                if action == 'add':
                    location = request.form.get('location')
                    max_capacity = request.form.get('max_capacity')
                    if not location or not max_capacity:
                        flash("Please provide both Location and Maximum Capacity.", "warning")
                    else:
                        try:
                            max_capacity = int(max_capacity)
                        except ValueError:
                            flash("Maximum Capacity must be an integer.", "warning")
                            return redirect(url_for('manage_rooms'))
                        sql = "INSERT INTO Room (Location, MaxRoomCapacity, ActiveFlag) VALUES (%s, %s, 1)"
                        cursor.execute(sql, (location, max_capacity))
                        conn.commit()
                        flash("Room added successfully.", "success")
                # ----------------
                # UPDATE Room
                # ----------------
                elif action == 'update':
                    room_id = request.form.get('room_id')
                    location = request.form.get('location')
                    max_capacity = request.form.get('max_capacity')
                    if not room_id or not location or not max_capacity:
                        flash("Missing fields for update.", "warning")
                    else:
                        try:
                            max_capacity = int(max_capacity)
                        except ValueError:
                            flash("Maximum Capacity must be an integer.", "warning")
                            return redirect(url_for('manage_rooms'))
                        sql = "UPDATE Room SET Location = %s, MaxRoomCapacity = %s WHERE RoomID = %s"
                        cursor.execute(sql, (location, max_capacity, room_id))
                        conn.commit()
                        flash("Room updated successfully.", "success")
                # ----------------
                # DELETE Room
                # ----------------
                elif action == 'delete':
                    room_id = request.form.get('room_id')
                    if not room_id:
                        flash("Missing Room ID for deletion.", "warning")
                    else:
                        sql = "DELETE FROM Room WHERE RoomID = %s"
                        cursor.execute(sql, (room_id,))
                        conn.commit()
                        flash("Room deleted successfully.", "success")
            # Read (List all Rooms)
            cursor.execute("SELECT * FROM Room")
            rooms = cursor.fetchall()
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Error in manage_rooms: {err}")
        flash(f"Database error: {err}", "danger")
        rooms = []
    finally:
        conn.close()
    
    return render_template('manage_rooms.html', rooms=rooms)


@app.route('/manage-lectures', methods=['GET', 'POST'])
def manage_lectures():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template('manage_lectures.html', lecturers=[], faculty_types=[])
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            if request.method == 'POST':
                action = request.form.get('action')
                # ----------------
                # CREATE (Add New Lecturer)
                # ----------------
                if action == 'add':
                    lecturer_name = request.form.get('lecturer_name')
                    faculty_type_id = request.form.get('faculty_type_id')
                    if not lecturer_name or not faculty_type_id:
                        flash("Please provide Lecturer Name and Faculty Type ID.", "warning")
                    else:
                        try:
                            faculty_type_id = int(faculty_type_id)
                        except ValueError:
                            flash("Faculty Type ID must be an integer.", "warning")
                            return redirect(url_for('manage_lectures'))
                        sql = "INSERT INTO Lecturer (LecturerName, FacultyTypeID, ActiveFlag) VALUES (%s, %s, 1)"
                        cursor.execute(sql, (lecturer_name, faculty_type_id))
                        conn.commit()
                        flash("Lecturer added successfully.", "success")
                # ----------------
                # UPDATE Lecturer
                # ----------------
                elif action == 'update':
                    lecturer_id = request.form.get('lecturer_id')
                    lecturer_name = request.form.get('lecturer_name')
                    faculty_type_id = request.form.get('faculty_type_id')
                    if not lecturer_id or not lecturer_name or not faculty_type_id:
                        flash("Missing fields for update.", "warning")
                    else:
                        try:
                            faculty_type_id = int(faculty_type_id)
                        except ValueError:
                            flash("Faculty Type ID must be an integer.", "warning")
                            return redirect(url_for('manage_lectures'))
                        sql = "UPDATE Lecturer SET LecturerName = %s, FacultyTypeID = %s WHERE LecturerID = %s"
                        cursor.execute(sql, (lecturer_name, faculty_type_id, lecturer_id))
                        conn.commit()
                        flash("Lecturer updated successfully.", "success")
                # ----------------
                # DELETE Lecturer
                # ----------------
                elif action == 'delete':
                    lecturer_id = request.form.get('lecturer_id')
                    if not lecturer_id:
                        flash("Missing Lecturer ID for deletion.", "warning")
                    else:
                        sql = "DELETE FROM Lecturer WHERE LecturerID = %s"
                        cursor.execute(sql, (lecturer_id,))
                        conn.commit()
                        flash("Lecturer deleted successfully.", "success")
            # Read (List all Lecturers) along with FacultyType info
            cursor.execute("""
                SELECT l.*, ft.FacultyTypeName 
                FROM Lecturer l 
                JOIN FacultyType ft ON l.FacultyTypeID = ft.FacultyTypeID
            """)
            lecturers = cursor.fetchall()
            # Also fetch all available faculty types for the add/update forms.
            cursor.execute("SELECT * FROM FacultyType")
            faculty_types = cursor.fetchall()
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Error in manage_lectures: {err}")
        flash(f"Database error: {err}", "danger")
        lecturers = []
        faculty_types = []
    finally:
        conn.close()
    
    return render_template('manage_lectures.html', lecturers=lecturers, faculty_types=faculty_types)


@app.route('/manage-courses', methods=['GET', 'POST'])
def manage_courses():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template('manage_courses.html', courses=[])
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            if request.method == 'POST':
                action = request.form.get('action')
                # ----------------
                # CREATE (Add New Course)
                # ----------------
                if action == 'add':
                    course_code = request.form.get('course_code')
                    course_name = request.form.get('course_name')
                    requirement_type = request.form.get('requirement_type')
                    credits = request.form.get('credits')
                    active_flag = request.form.get('active_flag', 1)  # default active_flag to 1
                    if not course_code or not course_name or not requirement_type or not credits:
                        flash("Please fill in all required fields for the new course.", "warning")
                    else:
                        try:
                            credits = float(credits)
                        except ValueError:
                            flash("Credits must be a number.", "warning")
                            return redirect(url_for('manage_courses'))
                        sql = """
                            INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (course_code, course_name, requirement_type, active_flag, credits))
                        conn.commit()
                        flash("Course added successfully.", "success")
                # ----------------
                # UPDATE Course
                # ----------------
                elif action == 'update':
                    course_id = request.form.get('course_id')
                    course_code = request.form.get('course_code')
                    course_name = request.form.get('course_name')
                    requirement_type = request.form.get('requirement_type')
                    credits = request.form.get('credits')
                    active_flag = request.form.get('active_flag', 1)
                    if not course_id or not course_code or not course_name or not requirement_type or not credits:
                        flash("Missing fields for update.", "warning")
                    else:
                        try:
                            credits = float(credits)
                        except ValueError:
                            flash("Credits must be a number.", "warning")
                            return redirect(url_for('manage_courses'))
                        sql = """
                            UPDATE Course 
                            SET CourseCode = %s, CourseName = %s, RequirementType = %s, ActiveFlag = %s, Credits = %s 
                            WHERE CourseID = %s
                        """
                        cursor.execute(sql, (course_code, course_name, requirement_type, active_flag, credits, course_id))
                        conn.commit()
                        flash("Course updated successfully.", "success")
                # ----------------
                # DELETE Course
                # ----------------
                elif action == 'delete':
                    course_id = request.form.get('course_id')
                    if not course_id:
                        flash("Missing Course ID for deletion.", "warning")
                    else:
                        sql = "DELETE FROM Course WHERE CourseID = %s"
                        cursor.execute(sql, (course_id,))
                        conn.commit()
                        flash("Course deleted successfully.", "success")
            # Read (List all Courses)
            cursor.execute("SELECT * FROM Course")
            courses = cursor.fetchall()
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Error in manage_courses: {err}")
        flash(f"Database error: {err}", "danger")
        courses = []
    finally:
        conn.close()
    
    return render_template('manage_courses.html', courses=courses)





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
                FROM UpdatedSessionSchedule  ss
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
                FROM UpdatedSessionSchedule 
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
                FROM UpdatedSessionSchedule  ss
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
    Pulls data from SessionAssignments + UpdatedSessionSchedule  => combined schedule.
    Converts TIME columns to "HH:MM" for StartTime/EndTime.
    Also includes CohortName so we can display it in the matrix.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in fetch_sessions_join_schedule.")
        return []
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql = """
                SELECT 
                  sa.SessionID,
                  sa.CourseCode,
                  sa.SessionType,
                  sa.LecturerName AS Lecturer,
                  sa.CohortName,                      -- <--- MISSING LINE PREVIOUSLY
                  sc.DayOfWeek,
                  sc.StartTime,
                  sc.EndTime,
                  sc.RoomName
                FROM SessionAssignments sa
                JOIN SessionSchedule sc 
                    ON sa.SessionID = sc.SessionID
                ORDER BY sa.SessionID
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error fetching sessions and schedule: {err}")
        rows = []
    finally:
        conn.close()

    # Convert TIME fields to "HH:MM"
    for r in rows:
        start_time = r["StartTime"]
        end_time   = r["EndTime"]
        r["StartTime"] = convert_time_to_hhmm(start_time)
        r["EndTime"]   = convert_time_to_hhmm(end_time)

    logging.info("Fetched sessions and schedule successfully.")
    return rows

def fetch_sessions_join_schedule_for_updated_schedule():
    """
    Pulls data from SessionAssignments + UpdatedSessionSchedule (staging timetable),
    joins with the Course table to include CourseName, and converts TIME columns to "HH:MM" strings.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in fetch_sessions_join_schedule.")
        return []
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            sql = """
                SELECT 
                  sa.SessionID,
                  sa.CourseCode,
                  c.CourseName,
                  sa.SessionType,
                  sa.LecturerName AS Lecturer,
                  sa.CohortName,
                  us.DayOfWeek,
                  us.StartTime,
                  us.EndTime,
                  us.RoomName
                FROM SessionAssignments sa
                JOIN UpdatedSessionSchedule us 
                  ON sa.SessionID = us.SessionID
                LEFT JOIN Course c
                  ON sa.CourseCode = c.CourseCode
                ORDER BY sa.SessionID
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error fetching sessions and updated schedule: {err}")
        rows = []
    finally:
        conn.close()

    # Convert TIME fields to "HH:MM"
    for r in rows:
        start_time = r["StartTime"]
        end_time   = r["EndTime"]
        r["StartTime"] = convert_time_to_hhmm(start_time)
        r["EndTime"]   = convert_time_to_hhmm(end_time)

    logging.info("Fetched sessions and updated schedule successfully.")
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
        return redirect(url_for('homepage'))
    
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
        return redirect(url_for('homepage'))
    
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
        return redirect(url_for('homepage'))
    
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
                        (CourseCode, LecturerName, CohortName, SessionType, Duration, NumberOfEnrollments, AdditionalStaff)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        course_code,
                        chosen_lecturer,
                        cohort_name,
                        session_type,
                        duration_str,
                        enrollments,
                        lecturer_intern  # Store Faculty Intern in AdditionalStaff
                    ))
    
                conn.commit()
                flash("Sessions saved for selected course!", "success")
    
            # GET request handling
            cursor.execute("SELECT CourseID, CourseCode, CourseName, Credits FROM Course WHERE ActiveFlag=1")
            courses_data = cursor.fetchall()
    
            cursor.execute("SELECT LecturerName FROM Lecturer WHERE ActiveFlag=1")
            lecturers_data = cursor.fetchall()
    
            cursor.execute("SELECT SessionTypeName FROM SessionType")
            session_types_raw = cursor.fetchall()
            session_types_data = [row[0] for row in session_types_raw] if session_types_raw else ['Lecture','Discussion']

            cursor.execute("SELECT Duration FROM Duration")
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
        return redirect(url_for('timetable'))
    
    return render_template('run_scheduler.html')


@app.route('/schedule_builder')
def schedule_builder():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template('schedule_builder.html', progress=0)

    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM Lecturer WHERE ActiveFlag = 1")
            active_lecturers = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) AS count FROM Room WHERE ActiveFlag = 1")
            active_rooms = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) AS count FROM SessionAssignments")
            assigned_sessions = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) AS count FROM StudentCourseSelection")
            selected_courses = cursor.fetchone()['count']

            progress = 0
            if active_lecturers > 0:
                progress = 1
            if active_rooms > 0:
                progress = 2
            if assigned_sessions > 0:
                progress = 3
            if selected_courses > 0:
                progress = 4

    finally:
        conn.close()

    return render_template('schedule_builder.html', progress=progress)

# ----------------------------------------------------
# Route: Course Selection
# ----------------------------------------------------
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    logging.info("Accessed /courses route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('homepage'))
    
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                # Retrieve list of course IDs from the form; these are strings so you might want to cast if needed.
                selected_course_ids = request.form.getlist('course_ids')
                logging.info(f"Selected courses: {selected_course_ids}")
                
                # Reset all courses to inactive.
                cursor.execute("UPDATE Course SET ActiveFlag = 0")
                
                # If some courses were selected, update them to active.
                if selected_course_ids:
                    placeholders = ','.join(['%s'] * len(selected_course_ids))
                    update_sql = f"UPDATE Course SET ActiveFlag = 1 WHERE CourseID IN ({placeholders})"
                    cursor.execute(update_sql, selected_course_ids)
                
                conn.commit()
                return redirect(url_for('courses'))
    
            # For GET, fetch all courses (including their active flag)
            cursor.execute("""
                SELECT CourseID, CourseCode, CourseName, Credits, ActiveFlag
                FROM Course
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
    return redirect(url_for('feasibility.feasibility_check'))




# ----------------------------------------------------
# Route: Student->Courses bridging
# ----------------------------------------------------
@app.route('/student_courses', methods=['GET', 'POST'])
def student_courses():
    logging.info("Accessed /student_courses route.")
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('homepage'))
    
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
                  UPDATE UpdatedSessionSchedule 
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
        return redirect(url_for('homepage'))
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Retrieve unassigned sessions with CourseName via LEFT JOIN with Course table
            cursor.execute("""
                SELECT u.*, c.CourseName
                FROM UnassignedSessions u
                LEFT JOIN Course c ON u.CourseCode = c.CourseCode
            """)
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
    excluding days already in the lecturer's existing schedule as well as days on which the course
    is already scheduled, and considering Friday prayer constraints.
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
            all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            assigned_days = lecturer_assigned_days(lecturer)
            logging.debug(f"Assigned days for lecturer {lecturer}: {assigned_days}")

            # --- NEW RULE: Exclude days already used by the course ---
            # Retrieve the course code for the session:
            cursor.execute("SELECT CourseCode FROM SessionAssignments WHERE SessionID = %s", (session_id,))
            course_row = cursor.fetchone()
            course_code = course_row["CourseCode"] if course_row else None
            course_days = set()
            if course_code:
                cursor.execute("""
                    SELECT DISTINCT ss.DayOfWeek
                    FROM UpdatedSessionSchedule  ss
                    JOIN SessionAssignments sa ON ss.SessionID = sa.SessionID
                    WHERE sa.CourseCode = %s
                """, (course_code,))
                rows = cursor.fetchall()
                course_days = {r["DayOfWeek"] for r in rows}
                logging.debug(f"Existing scheduled days for course {course_code}: {course_days}")

            # Exclude both lecturer assigned days and course scheduled days
            excluded_days = set(assigned_days) | course_days
            possible_days = [day for day in all_days if day not in excluded_days]
            logging.debug(f"Possible alternative days after exclusion: {possible_days}")

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
# Route: Resolve Conflict -> move from UnassignedSessions -> UpdatedSessionSchedule 
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
                SELECT COUNT(*) FROM UpdatedSessionSchedule 
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
                SELECT COUNT(*) FROM UpdatedSessionSchedule  ss
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
    
            # Insert into UpdatedSessionSchedule 
            insert_sql = """
                INSERT INTO UpdatedSessionSchedule  (SessionID, DayOfWeek, StartTime, EndTime, RoomName)
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
                JOIN UpdatedSessionSchedule  sc ON sa.SessionID = sc.SessionID
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

@app.route('/timetable', methods=['GET'])
def timetable():
    logging.info("Accessed /timetable route.")
    try:
        sessions = fetch_sessions_join_schedule_for_updated_schedule()
        logging.info(f"Fetched {len(sessions)} sessions for timetable.")
        
        # Fetch all active rooms
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for('homepage'))
        
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
    4: ['CE', 'ENGR', 'CS'],    # Computer Engineering
    5: ['MECH'],          # Mechatronics Engineering (Assumed prefix)
    6: ['ME', 'ENGR'],    # Mechanical Engineering
    7: ['EE', 'ENGR'],    # Electrical and Electronic Engineering
    8: ['LAW'],           # Law with Public Policy (Assumed prefix)
    # Add more mappings as necessary
}

# ----------------------------------------------------
# ROUTE: Student Timetables Page
# ----------------------------------------------------
@app.route('/student_timetables')
def student_timetables():
    """
    Student Timetables page.
    Displays a list of all students with links to their individual timetables.
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        logging.error("Failed to connect to the database while accessing the Student Timetables page.")
        return render_template('student_timetables.html', students=[])
    
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
    
    return render_template('student_timetables.html', students=students)

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
        return redirect(url_for('student_timetables'))
    
    # Establish database connection
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        logging.error(f"Failed to connect to the database for StudentID {student_id}.")
        return redirect(url_for('student_timetables'))
    
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
                return redirect(url_for('student_timetables'))
            
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
                return redirect(url_for('student_timetables'))

            # ---------------------------------------------------------------------
            # UPDATED SECTION: Fetch ALL Active Elective Courses for This Day
            # ---------------------------------------------------------------------
            cursor.execute("""
                SELECT c.CourseCode, c.CourseName,
                    sa.LecturerName, sa.CohortName,
                    ss.RoomName, ss.StartTime, ss.EndTime
                FROM Course c
                JOIN SessionAssignments sa ON c.CourseCode = sa.CourseCode
                JOIN UpdatedSessionSchedule ss ON sa.SessionID = ss.SessionID
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
            cursor.execute("""
                SELECT sa.CourseCode,
                       c.CourseName,
                       sa.LecturerName,
                       sa.CohortName,
                       ss.StartTime,
                       ss.EndTime,
                       ss.RoomName
                FROM SessionAssignments sa
                JOIN UpdatedSessionSchedule ss ON sa.SessionID = ss.SessionID
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

    if not major_elective_details:
        logging.warning(f"No Major Electives found for StudentID {student_id} on {day_of_week}.")
    if not non_major_elective_details:
        logging.warning(f"No Non-Major Electives found for StudentID {student_id} on {day_of_week}.")
    
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

# =========================================
#  Apply Break Route
# =========================================
@app.route('/apply_break', methods=['POST'])
def apply_break():
    """
    Enforces a 15-minute gap for all sessions in the given (roomName, dayOfWeek).
    Expects JSON payload: { "day": <str>, "roomName": <str> }
    Returns JSON: { "success": true/false, "message": "..." }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    day_of_week = data.get("day")
    room_name = data.get("roomName")

    if not day_of_week or not room_name:
        return jsonify({"success": False, "message": "Missing day_of_week or room_name."}), 400

    try:
        # Enforce the 15-min rule for that room & day
        enforce_15_min_break(room_name, day_of_week)
        return jsonify({"success": True, "message": "Break applied successfully."}), 200
    except Exception as e:
        logging.error(f"Error applying 15-min break: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def to_time(value):
    """
    Ensure 'value' is a datetime.time. If it's a timedelta, convert it.
    If it's already a time, just return it.
    """
    if isinstance(value, time):
        return value
    elif isinstance(value, timedelta):
        # Convert 'timedelta' to a 'time' by adding it to datetime.min
        return (datetime.min + value).time()
    else:
        # Return None or raise an error if it's neither time nor timedelta
        return None

def enforce_15_min_break(room_name, day_of_week):
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed.")

    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)

        # 1) Select sessions
        sql = """
            SELECT ScheduleID, StartTime, EndTime
            FROM UpdatedSessionSchedule 
            WHERE RoomName = %s
              AND DayOfWeek = %s
            ORDER BY StartTime
        """
        cursor.execute(sql, (room_name, day_of_week))
        sessions = cursor.fetchall()

        last_end = None
        for row in sessions:
            sched_id = row["ScheduleID"]
            s_start  = to_time(row["StartTime"])  # ensure it's time
            s_end    = to_time(row["EndTime"])    # ensure it's time

            if s_start is None or s_end is None:
                # If either is invalid, skip or raise an error
                raise ValueError("StartTime/EndTime not recognized as time or timedelta.")

            if last_end is not None:
                # min_start = last_end + 15 min
                min_start = (datetime.combine(datetime.today(), last_end)
                             + timedelta(minutes=15)).time()

                if s_start < min_start:
                    # preserve duration in seconds
                    duration_sec = (
                        datetime.combine(datetime.today(), s_end)
                        - datetime.combine(datetime.today(), s_start)
                    ).total_seconds()

                    new_start = min_start
                    new_end_dt = (datetime.combine(datetime.today(), new_start)
                                  + timedelta(seconds=duration_sec))
                    new_end = new_end_dt.time()

                    # DB update
                    update_sql = """
                        UPDATE UpdatedSessionSchedule 
                        SET StartTime = %s, EndTime = %s
                        WHERE ScheduleID = %s
                    """
                    cursor.execute(update_sql, (new_start, new_end, sched_id))

                    s_start = new_start
                    s_end   = new_end

            # Update last_end
            last_end = s_end

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def fetch_plan_by_course():
    """
    Returns a dict keyed by CourseCode, where each value is a list of
    { MajorName, YearNumber, SemesterNumber, SubType }
    describing which Majors/Years/Semesters include that course.
    """
    plan_map = defaultdict(list)
    
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database in fetch_plan_by_course.")
        return plan_map
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Pull ProgramPlan + Major + Course info
            # We'll also get the MajorName directly to display.
            sql = """
                SELECT 
                  m.MajorName,
                  p.YearNumber,
                  p.SemesterNumber,
                  IFNULL(p.SubType, '') AS SubType,
                  p.CourseCode
                FROM ProgramPlan p
                JOIN Major m ON p.MajorID = m.MajorID
                -- We could also join Course c ON p.CourseCode = c.CourseCode
                -- if we need the course name or other fields
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            for row in rows:
                ccode = row["CourseCode"]
                plan_map[ccode].append({
                    "MajorName": row["MajorName"],
                    "YearNumber": row["YearNumber"],
                    "SemesterNumber": row["SemesterNumber"],
                    "SubType": row["SubType"]
                })
    
    except mysql.connector.Error as err:
        logging.error(f"Error in fetch_plan_by_course: {err}")
        # Return what we have so far (likely empty)
    finally:
        conn.close()
    
    return plan_map



@app.route('/conflict_free_matrix', methods=['GET'])
def conflict_free_matrix():
    """
    Displays a matrix timetable with:
      - Rows = distinct start times from scheduled sessions
      - Columns = Monday–Friday
      - Cells = sessions (course code, cohort, room, etc.)
    The "In Plan" information is color-coded by year using the first plan entry’s YearNumber.
    """
    logging.info("Accessed /conflict_free_matrix route.")
    
    # 1) Fetch all sessions
    sessions = fetch_sessions_join_schedule_for_updated_schedule()
    
    # 2) Fetch ProgramPlan info and attach it to each session
    plan_by_course = fetch_plan_by_course()
    for s in sessions:
        code = s.get("CourseCode", "")
        s["PlanInfo"] = plan_by_course.get(code, [])
    
    # 3) Define the days
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # 4) Compute distinct timeslots (using session start times)
    timeslot_set = set()
    for sess in sessions:
        timeslot_set.add(sess["StartTime"])
    # Sort timeslot strings (assumes format "HH:MM")
    timeslots = sorted(timeslot_set)

    # 5) Bucket sessions by (day, start time)
    matrix_data = { day: { t: [] for t in timeslots } for day in days }
    for sess in sessions:
        day = sess["DayOfWeek"]
        if day in days and sess["StartTime"] in timeslots:
            matrix_data[day][sess["StartTime"]].append(sess)
    
    # 6) Build color maps for rooms (cohort coloring is removed)
    import random
    random.seed(42)
    # (We still compute cohort_colors if needed for tooltips, but they are not used for background)
    all_rooms = set(sess.get("RoomName", "Unknown") for sess in sessions)
    palette2 = [
        "#ffcccb", "#ffe4b5", "#ffffe0", "#d3ffd3",
        "#cce5ff", "#e5ccff", "#f5e6e8", "#e2f0d9",
        "#d1ecf1", "#fefefe"
    ]
    random.shuffle(palette2)
    room_colors = {}
    j = 0
    for r in sorted(all_rooms):
        room_colors[r] = palette2[j % len(palette2)]
        j += 1

    # Define year_colors for plan info (for example: Year 1 = red-ish, Year 2 = blue, etc.)
    year_colors = {1: '#f86c6b', 2: '#20a8d8', 3: '#4dbd74', 4: '#ffc107'}

    return render_template(
        'conflict_free_matrix.html',
        days=days,
        timeslots=timeslots,
        matrix_data=matrix_data,
        room_colors=room_colors,
        year_colors=year_colors
    )

@app.route('/student_timetable_grid/<int:student_id>', methods=['GET'])
def student_timetable_grid(student_id):
    """
    Displays a student’s timetable as a grid.
    The columns are days of the week (Monday–Friday) and the rows are the distinct start times of sessions.
    The grid shows both regular sessions (based on the student’s course selections)
    and elective sessions (with an added field to indicate whether they are a Major or Non-Major elective).
    """
    logging.info(f"Accessed /student_timetable_grid route for StudentID {student_id}")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Establish database connection
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for("homepage"))

    try:
        with conn.cursor(dictionary=True) as cursor:
            # (1) Fetch Student Information
            cursor.execute("""
                SELECT s.StudentID, s.MajorID, m.MajorName, s.YearNumber
                FROM Student s
                JOIN Major m ON s.MajorID = m.MajorID
                WHERE s.StudentID = %s
            """, (student_id,))
            student_info = cursor.fetchone()
            if not student_info:
                flash("Student not found.", "danger")
                return redirect(url_for("homepage"))

            major_id   = student_info["MajorID"]
            major_name = student_info["MajorName"]
            year_num   = student_info["YearNumber"]
            student_label = f"StudentID {student_id}, {ordinal(year_num)}-year {major_name}"

            # (2) Get major prefixes from mapping (used to distinguish elective types)
            major_prefixes = major_prefix_mapping.get(major_id, [])
            if not major_prefixes:
                flash("No major prefixes defined for this student’s major.", "danger")
                return redirect(url_for("homepage"))

            # (3) Fetch regular (non-elective) sessions for the student
            cursor.execute("""
                SELECT sa.CourseCode,
                       c.CourseName,
                       sa.LecturerName,
                       sa.CohortName,
                       ss.StartTime,
                       ss.EndTime,
                       ss.RoomName,
                       ss.DayOfWeek
                FROM SessionAssignments sa
                JOIN UpdatedSessionSchedule ss ON sa.SessionID = ss.SessionID
                JOIN Course c ON sa.CourseCode = c.CourseCode
                WHERE sa.CourseCode IN (
                    SELECT DISTINCT scc.CourseCode
                    FROM StudentCourseSelection scc
                    WHERE scc.StudentID = %s
                )
                  AND c.RequirementType NOT LIKE '%Elective%'
                  AND c.ActiveFlag = 1
                ORDER BY ss.DayOfWeek, ss.StartTime
            """, (student_id,))
            regular_sessions = cursor.fetchall()

            # (4) Fetch elective sessions (for all days)
            cursor.execute("""
                SELECT c.CourseCode,
                       c.CourseName,
                       sa.LecturerName,
                       sa.CohortName,
                       ss.StartTime,
                       ss.EndTime,
                       ss.RoomName,
                       ss.DayOfWeek
                FROM Course c
                JOIN SessionAssignments sa ON c.CourseCode = sa.CourseCode
                JOIN UpdatedSessionSchedule ss ON sa.SessionID = ss.SessionID
                WHERE c.RequirementType LIKE '%Elective%'
                  AND c.ActiveFlag = 1
                ORDER BY c.CourseCode, ss.DayOfWeek, ss.StartTime
            """)
            elective_sessions = cursor.fetchall()

            # (5) Process elective sessions: label each as "Major Elective" or "Non-Major Elective"
            for sess in elective_sessions:
                course_code = sess["CourseCode"]
                if any(course_code.startswith(prefix) for prefix in major_prefixes):
                    sess["ElectiveType"] = "Major Elective"
                else:
                    sess["ElectiveType"] = "Non-Major Elective"

            # (6) Combine sessions
            all_sessions = regular_sessions + elective_sessions

            # (7) Convert StartTime and EndTime to readable "HH:MM" strings.
            for sess in all_sessions:
                if hasattr(sess["StartTime"], "total_seconds"):
                    sess["StartTime"] = convert_timedelta_to_hhmm(sess["StartTime"])
                else:
                    sess["StartTime"] = str(sess["StartTime"])[:5]
                if hasattr(sess["EndTime"], "total_seconds"):
                    sess["EndTime"] = convert_timedelta_to_hhmm(sess["EndTime"])
                else:
                    sess["EndTime"] = str(sess["EndTime"])[:5]

            # (8) Determine distinct time slots (rows) based on session start times
            timeslot_set = { sess["StartTime"] for sess in all_sessions }
            timeslots = sorted(timeslot_set)

            # (9) Bucket sessions into a grid: for each day and each timeslot, list any sessions that start then.
            matrix_data = { day: { t: [] for t in timeslots } for day in days }
            for sess in all_sessions:
                day = sess["DayOfWeek"]
                start_time = sess["StartTime"]
                if day in days and start_time in timeslots:
                    matrix_data[day][start_time].append(sess)

            # (10) Build a cohort_colors mapping from the sessions.
            cohorts = {sess["CohortName"] for sess in all_sessions if sess.get("CohortName")}
            color_palette = [
                "#FF6666", "#66B3FF", "#99FF99", "#FFCC66", "#C0C0C0", "#FF99CC",
                "#FF6666", "#FFB366", "#FFFF66", "#B3FF66", "#66FF66", "#66FFB3",
                "#66FFFF", "#66B3FF", "#6666FF", "#B366FF", "#FF66FF", "#FF66B3",
                "#FF6666", "#FF8C66", "#FFB366", "#FFD966", "#FFFF66", "#D9FF66",
                "#B3FF66", "#8CFF66", "#66FF66", "#66FF8C", "#66FFB3", "#66FFD9"
            ]
            cohort_colors = {}
            for i, cohort in enumerate(sorted(cohorts)):
                cohort_colors[cohort] = color_palette[i % len(color_palette)]
    except mysql.connector.Error as err:
        logging.error(f"Database error in student_timetable_grid: {err}")
        flash("An error occurred while fetching timetable data.", "danger")
        return redirect(url_for("homepage"))
    finally:
        conn.close()

    return render_template(
        "student_timetable_grid.html",
        student_id=student_id,
        student_label=student_label,
        matrix_data=matrix_data,
        days=days,
        timeslots=timeslots,
        cohort_colors=cohort_colors
    )

@app.route('/manage_students', methods=['GET', 'POST'])
def manage_students():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        # Pass empty lists so the template can handle no data gracefully.
        return render_template('manage_students.html', students=[], program_plans=[], majors=[])
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Handle POST submissions for both Students and ProgramPlan entries.
            if request.method == 'POST':
                entity = request.form.get('entity')  # should be "student" or "program_plan"
                action = request.form.get('action')    # "add", "update", "delete"
                
                if entity == 'student':
                    if action == 'add':
                        major_id = request.form.get('major_id')
                        year_number = request.form.get('year_number')
                        if not major_id or not year_number:
                            flash("Please provide both Major and Year Number.", "warning")
                        else:
                            try:
                                major_id = int(major_id)
                                year_number = int(year_number)
                            except ValueError:
                                flash("Major and Year Number must be integers.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = "INSERT INTO Student (MajorID, YearNumber) VALUES (%s, %s)"
                            cursor.execute(sql, (major_id, year_number))
                            conn.commit()
                            flash("Student added successfully.", "success")
                    
                    elif action == 'update':
                        student_id = request.form.get('student_id')
                        major_id = request.form.get('major_id')
                        year_number = request.form.get('year_number')
                        if not student_id or not major_id or not year_number:
                            flash("Please provide Student ID, Major and Year Number for update.", "warning")
                        else:
                            try:
                                student_id = int(student_id)
                                major_id = int(major_id)
                                year_number = int(year_number)
                            except ValueError:
                                flash("IDs must be integers.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = "UPDATE Student SET MajorID = %s, YearNumber = %s WHERE StudentID = %s"
                            cursor.execute(sql, (major_id, year_number, student_id))
                            conn.commit()
                            flash("Student updated successfully.", "success")
                    
                    elif action == 'delete':
                        student_id = request.form.get('student_id')
                        if not student_id:
                            flash("Student ID is required for deletion.", "warning")
                        else:
                            try:
                                student_id = int(student_id)
                            except ValueError:
                                flash("Student ID must be an integer.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = "DELETE FROM Student WHERE StudentID = %s"
                            cursor.execute(sql, (student_id,))
                            conn.commit()
                            flash("Student deleted successfully.", "success")
                
                elif entity == 'program_plan':
                    if action == 'add':
                        major_id = request.form.get('major_id')
                        year_number = request.form.get('year_number')
                        semester_number = request.form.get('semester_number')
                        subtype = request.form.get('subtype')  # can be empty
                        course_code = request.form.get('course_code')
                        if not major_id or not year_number or not semester_number or not course_code:
                            flash("Please provide Major, Year Number, Semester Number, and Course Code.", "warning")
                        else:
                            try:
                                major_id = int(major_id)
                                year_number = int(year_number)
                                semester_number = int(semester_number)
                            except ValueError:
                                flash("Major, Year, and Semester numbers must be integers.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = """
                                INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (major_id, year_number, semester_number, subtype, course_code))
                            conn.commit()
                            flash("Program plan entry added successfully.", "success")
                    
                    elif action == 'update':
                        plan_id = request.form.get('plan_id')
                        major_id = request.form.get('major_id')
                        year_number = request.form.get('year_number')
                        semester_number = request.form.get('semester_number')
                        subtype = request.form.get('subtype')
                        course_code = request.form.get('course_code')
                        if not plan_id or not major_id or not year_number or not semester_number or not course_code:
                            flash("Please provide all fields for updating program plan entry.", "warning")
                        else:
                            try:
                                plan_id = int(plan_id)
                                major_id = int(major_id)
                                year_number = int(year_number)
                                semester_number = int(semester_number)
                            except ValueError:
                                flash("IDs must be integers.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = """
                                UPDATE ProgramPlan 
                                SET MajorID = %s, YearNumber = %s, SemesterNumber = %s, SubType = %s, CourseCode = %s
                                WHERE ProgramPlanID = %s
                            """
                            cursor.execute(sql, (major_id, year_number, semester_number, subtype, course_code, plan_id))
                            conn.commit()
                            flash("Program plan entry updated successfully.", "success")
                    
                    elif action == 'delete':
                        plan_id = request.form.get('plan_id')
                        if not plan_id:
                            flash("Program plan ID is required for deletion.", "warning")
                        else:
                            try:
                                plan_id = int(plan_id)
                            except ValueError:
                                flash("Program plan ID must be an integer.", "warning")
                                return redirect(url_for('manage_students'))
                            sql = "DELETE FROM ProgramPlan WHERE ProgramPlanID = %s"
                            cursor.execute(sql, (plan_id,))
                            conn.commit()
                            flash("Program plan entry deleted successfully.", "success")
            # After handling any POST operations, fetch current data to display.
            # 1) Fetch all students (with Major name)
            cursor.execute("""
                SELECT s.StudentID, s.MajorID, s.YearNumber, m.MajorName
                FROM Student s
                JOIN Major m ON s.MajorID = m.MajorID
                ORDER BY s.StudentID
            """)
            students = cursor.fetchall()
            # 2) Fetch all program plan entries (with Major name)
            cursor.execute("""
                SELECT pp.ProgramPlanID, pp.MajorID, pp.YearNumber, pp.SemesterNumber, pp.SubType, pp.CourseCode, m.MajorName
                FROM ProgramPlan pp
                JOIN Major m ON pp.MajorID = m.MajorID
                ORDER BY pp.ProgramPlanID
            """)
            program_plans = cursor.fetchall()
            # 3) Fetch list of majors for use in dropdowns.
            cursor.execute("SELECT MajorID, MajorName FROM Major")
            majors = cursor.fetchall()
    except mysql.connector.Error as err:
        conn.rollback()
        logging.error(f"Error in /manage_students: {err}")
        flash(f"Database error: {err}", "danger")
        students = []
        program_plans = []
        majors = []
    finally:
        conn.close()
    
    return render_template('manage_students.html', students=students, program_plans=program_plans, majors=majors)

@app.route('/save_updated_timetable', methods=['POST'])
def save_updated_timetable():
    """
    Receives JSON data for updated session placements and updates the UpdatedSessionSchedule.
    Expected JSON: a list of objects containing:
      { "SessionID": ..., "DayOfWeek": ..., "StartTime": ..., "EndTime": ..., "RoomName": ... }
    """
    data = request.json
    app.logger.info("Received updated timetable data for staging.")
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 500
    try:
        with conn.cursor() as cursor:
            for sess in data:
                sid  = sess["SessionID"]
                day  = sess["DayOfWeek"]
                st   = sess["StartTime"]
                en   = sess["EndTime"]
                room = sess["RoomName"]
                sql = """
                  UPDATE UpdatedSessionSchedule
                  SET DayOfWeek = %s, StartTime = %s, EndTime = %s, RoomName = %s
                  WHERE SessionID = %s
                """
                cursor.execute(sql, (day, st, en, room, sid))
            conn.commit()
            app.logger.info(f"Updated staging timetable for {len(data)} sessions.")
        return jsonify({"message": "Staging timetable saved successfully."}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        app.logger.error(f"Error saving updated timetable: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/approve_updated_timetable', methods=['POST'])
def approve_updated_timetable():
    """
    Copies the rows from UpdatedSessionSchedule into SessionSchedule.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 500
    try:
        with conn.cursor() as cursor:
            # Option 1: Update the SessionSchedule table based on the staging table
            sql = """
              UPDATE SessionSchedule s
              JOIN UpdatedSessionSchedule u ON s.SessionID = u.SessionID
              SET s.DayOfWeek = u.DayOfWeek,
                  s.StartTime = u.StartTime,
                  s.EndTime = u.EndTime,
                  s.RoomName = u.RoomName
            """
            cursor.execute(sql)
            conn.commit()
            return jsonify({"message": "Timetable approved and updated successfully."}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()


# ----------------------------------------------------
# Helper: Convert value to "HH:MM" string.
def convert_to_time(t):
    if isinstance(t, timedelta):
        # Convert timedelta to time by adding to datetime.min
        return (datetime.min + t).strftime("%H:%M")
    elif isinstance(t, str):
        # If it's already a string, assume "HH:MM" or "HH:MM:SS" and take first 5 characters.
        return t[:5]
    else:
        return str(t)

# ----------------------------------------------------
# Step 1: Load Timetable Data from the Staging Table
# ----------------------------------------------------
def get_timetable_data():
    password = "Naakey057@"
    encoded_password = quote_plus(password)  # Converts "@" to "%40"
    engine = create_engine(f'mysql+mysqlconnector://root:{encoded_password}@localhost/schedulai')
    query = """
    SELECT 
      sa.SessionID,
      sa.CourseCode,
      sa.SessionType,
      sa.LecturerName AS Lecturer,
      sa.CohortName,
      us.DayOfWeek,
      us.StartTime,
      us.EndTime,
      us.RoomName
    FROM SessionAssignments sa
    JOIN UpdatedSessionSchedule us ON sa.SessionID = us.SessionID
    ORDER BY sa.SessionID
    """
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        logging.error("Error fetching timetable data: " + str(e))
        return pd.DataFrame()

# ----------------------------------------------------
# Step 2: Evaluation Functions (Marking Scheme) with Conflict Details
# ----------------------------------------------------
def compute_conflicts(df):
    """
    Compute hard constraint violations by counting overlapping sessions per room and per lecturer.
    Returns:
      - room_conflict_count: total count of room conflicts
      - lecturer_conflict_count: total count of lecturer conflicts
      - room_conflict_details: list of dicts with details about each room conflict
      - lecturer_conflict_details: list of dicts with details about each lecturer conflict
    """
    room_conflict_details = []
    lecturer_conflict_details = []
    
    # Convert StartTime and EndTime into datetime objects using our helper.
    df['Start_dt'] = df['StartTime'].apply(lambda t: datetime.strptime(convert_to_time(t), "%H:%M"))
    df['End_dt'] = df['EndTime'].apply(lambda t: datetime.strptime(convert_to_time(t), "%H:%M"))
    
    # Room conflicts: group by Day and RoomName
    for (day, room), group in df.groupby(['DayOfWeek', 'RoomName']):
        sessions = group.sort_values('Start_dt')
        for i in range(len(sessions) - 1):
            current = sessions.iloc[i]
            next_sess = sessions.iloc[i + 1]
            if current['End_dt'] > next_sess['Start_dt']:
                room_conflict_details.append({
                    'day': day,
                    'room': room,
                    'conflict_between': [current['SessionID'], next_sess['SessionID']],
                    'current_end': current['End_dt'].strftime("%H:%M"),
                    'next_start': next_sess['Start_dt'].strftime("%H:%M")
                })
                
    # Lecturer conflicts: group by Day and Lecturer
    for (day, lecturer), group in df.groupby(['DayOfWeek', 'Lecturer']):
        sessions = group.sort_values('Start_dt')
        for i in range(len(sessions) - 1):
            current = sessions.iloc[i]
            next_sess = sessions.iloc[i + 1]
            if current['End_dt'] > next_sess['Start_dt']:
                lecturer_conflict_details.append({
                    'day': day,
                    'lecturer': lecturer,
                    'conflict_between': [current['SessionID'], next_sess['SessionID']],
                    'current_end': current['End_dt'].strftime("%H:%M"),
                    'next_start': next_sess['Start_dt'].strftime("%H:%M"),
                    'current_course': current['CourseCode'],
                    'next_course': next_sess['CourseCode'],
                    'current_cohort': current['CohortName'],
                    'next_cohort': next_sess['CohortName'],
                    'current_room': current['RoomName'],
                    'next_room': next_sess['RoomName'],
                    'current_session_type': current['SessionType'],
                    'next_session_type': next_sess['SessionType']
                })
                
    room_conflict_count = len(room_conflict_details)
    lecturer_conflict_count = len(lecturer_conflict_details)
    return room_conflict_count, lecturer_conflict_count, room_conflict_details, lecturer_conflict_details

def compute_room_utilization(df):
    """Compute utilization as fraction of available time booked.
       Assume available time per day is 540 minutes (from 08:00 to 17:00)."""
    total_minutes = 540
    utilization = {}
    for (day, room), group in df.groupby(['DayOfWeek', 'RoomName']):
        booked = 0
        for idx, row in group.iterrows():
            start = datetime.strptime(convert_to_time(row['StartTime']), "%H:%M")
            end = datetime.strptime(convert_to_time(row['EndTime']), "%H:%M")
            booked += (end - start).seconds / 60
        utilization[(day, room)] = booked / total_minutes
    return utilization

def compute_lecturer_load(df):
    """Compute total scheduled minutes per lecturer per day."""
    load = {}
    for (day, lecturer), group in df.groupby(['DayOfWeek', 'Lecturer']):
        total = 0
        for idx, row in group.iterrows():
            start = datetime.strptime(convert_to_time(row['StartTime']), "%H:%M")
            end = datetime.strptime(convert_to_time(row['EndTime']), "%H:%M")
            total += (end - start).seconds / 60
        load[(day, lecturer)] = total
    return load

def grade_schedule(room_conflicts, lecturer_conflicts, utilization, load):
    """Combine penalties from hard and soft constraints to assign a total score and letter grade.
       Lower score is better."""
    penalty = room_conflicts * 50 + lecturer_conflicts * 50
    # Soft constraint: ideally room utilization ~0.7
    util_penalty = sum([abs(u - 0.7) * 5 for u in utilization.values()])
    # Soft constraint: ideally lecturer load <= 270 minutes (4.5 hours) per day
    load_penalty = sum([max(0, l - 270) * 0.25 for l in load.values()])
    total_score = penalty + util_penalty + load_penalty
    if total_score <= 150:
        grade = "A"
    elif total_score <= 200:
        grade = "B"
    elif total_score <= 250:
        grade = "C"
    elif total_score <= 300:
        grade = "D"
    else:
        grade = "E"
    return total_score, grade

# ----------------------------------------------------
# Step 3: AI/ML – Anomaly Detection on Lecturer Load
# ----------------------------------------------------
def perform_anomaly_detection(load):
    """Uses k-means clustering on lecturer load to flag potential overwork.
       Returns a DataFrame of anomalies."""
    df_load = pd.DataFrame(list(load.items()), columns=['Day_Lecturer', 'Load'])
    if df_load.empty:
        return df_load
    kmeans = KMeans(n_clusters=3, random_state=0)
    df_load['Cluster'] = kmeans.fit_predict(df_load[['Load']])
    # Identify which cluster has the higher average load
    cluster_means = df_load.groupby('Cluster')['Load'].mean()
    overworked_cluster = cluster_means.idxmax()
    anomalies = df_load[df_load['Cluster'] == overworked_cluster]
    return anomalies

# ----------------------------------------------------
# Step 3: Generate an Analysis Report (NLG)
# ----------------------------------------------------
def generate_analysis_report(total_score, grade, room_conflicts, lecturer_conflicts, utilization, load,
                             room_conflict_details, lecturer_conflict_details):
    template_str = """
    <h2>Timetable Analysis Report</h2>
    <p><strong>Hard Constraint Violations:</strong></p>
    <ul>
      <li>Room Conflicts: {{ room_conflicts }} 
          {% if room_conflict_details|length > 0 %}
            <ul>
            {% for conflict in room_conflict_details %}
              <li>Day: {{ conflict.day }}, Room: {{ conflict.room }}, 
                  Conflict between sessions {{ conflict.conflict_between[0] }} and {{ conflict.conflict_between[1] }},
                  (Ends at {{ conflict.current_end }}, Starts at {{ conflict.next_start }})</li>
            {% endfor %}
            </ul>
          {% endif %}
      </li>
      <li>Lecturer Conflicts: {{ lecturer_conflicts }} 
          {% if lecturer_conflict_details|length > 0 %}
            <ul>
            {% for conflict in lecturer_conflict_details %}
              <li>Day: {{ conflict.day }}, Lecturer: {{ conflict.lecturer }}, 
                  Conflict between sessions {{ conflict.conflict_between[0] }} and {{ conflict.conflict_between[1] }},
                  (Ends at {{ conflict.current_end }}, Starts at {{ conflict.next_start }})</li>
            {% endfor %}
            </ul>
          {% endif %}
      </li>
    </ul>
    <p><strong>Overall Evaluation:</strong></p>
    <ul>
      <li>Total Score: {{ total_score }}</li>
      <li>Assigned Grade: {{ grade }}</li>
    </ul>
    """
    template = Template(template_str)
    return template.render(
        room_conflicts=room_conflicts,
        lecturer_conflicts=lecturer_conflicts,
        total_score=total_score,
        grade=grade,
        utilization=utilization,
        load=load,
        room_conflict_details=room_conflict_details,
        lecturer_conflict_details=lecturer_conflict_details
    )

# ----------------------------------------------------
# Step 4: Visualization Dashboard (Generate Charts)
# ----------------------------------------------------
def create_visualizations(utilization, load):
    # Room Utilization Chart
    fig1, ax1 = plt.subplots(figsize=(8,4))
    room_keys = [f"{day} - {room}" for (day, room) in utilization.keys()]
    util_vals = list(utilization.values())
    ax1.barh(room_keys, util_vals)
    ax1.set_xlabel("Utilization Fraction")
    ax1.set_title("Room Utilization")
    buf1 = io.BytesIO()
    plt.tight_layout()
    fig1.savefig(buf1, format='png')
    buf1.seek(0)
    room_util_img = base64.b64encode(buf1.getvalue()).decode('utf8')
    plt.close(fig1)

    # Lecturer Load Chart
    fig2, ax2 = plt.subplots(figsize=(8,4))
    lecturer_keys = [f"{day} - {lecturer}" for (day, lecturer) in load.keys()]
    load_vals = list(load.values())
    ax2.barh(lecturer_keys, load_vals, color='orange')
    ax2.set_xlabel("Minutes")
    ax2.set_title("Lecturer Load")
    buf2 = io.BytesIO()
    plt.tight_layout()
    fig2.savefig(buf2, format='png')
    buf2.seek(0)
    lecturer_load_img = base64.b64encode(buf2.getvalue()).decode('utf8')
    plt.close(fig2)

    return room_util_img, lecturer_load_img

# ----------------------------------------------------
# Flask Endpoint: /analyze_timetable
# ----------------------------------------------------

@app.route('/analyze_timetable', methods=['GET'])
def analyze_timetable():
    # Step 1: Load data
    df = get_timetable_data()
    if df.empty:
        return "No timetable data available.", 500

    # Step 2: Evaluate conflicts and soft constraints.
    room_conflicts, lecturer_conflicts, room_conflict_details, lecturer_conflict_details = compute_conflicts(df)
    utilization = compute_room_utilization(df)
    load = compute_lecturer_load(df)
    
    # --- Compute Lecturer Load Context ---
    # Build grouped lecturer load data for summary and table:
    lecturer_load_groups = {"light": [], "moderate": [], "heavy": []}
    lecturer_load_table = []
    for (day, lecturer), minutes in load.items():
        # Add to table (this could be used for the interactive table)
        lecturer_load_table.append({"lecturer": lecturer, "day": day, "load": minutes})
        # Categorize load based on thresholds (Light: 0-90, Moderate: 91-180, Heavy: 181+)
        if minutes <= 90:
            lecturer_load_groups["light"].append({"lecturer": lecturer, "load": minutes})
        elif minutes <= 180:
            lecturer_load_groups["moderate"].append({"lecturer": lecturer, "load": minutes})
        else:
            lecturer_load_groups["heavy"].append({"lecturer": lecturer, "load": minutes})
    
    # Build pie chart data for lecturer load distribution.
    lecturer_load_pie_data = {
         "labels": ["Light", "Moderate", "Heavy"],
         "data": [
             len(lecturer_load_groups["light"]),
             len(lecturer_load_groups["moderate"]),
             len(lecturer_load_groups["heavy"])
         ]
    }
    
    # --- Compute Room Utilization Context ---
    days_order = ['Friday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
    room_to_util = {}
    for (day, room), util in utilization.items():
        if room not in room_to_util:
            room_to_util[room] = {}
        room_to_util[room][day] = util
    utilization_by_day = []
    for room, day_utils in room_to_util.items():
        # Ensure each day is present (defaulting to 0 if missing)
        util_dict = {day: day_utils.get(day, 0) for day in days_order}
        utilization_by_day.append({'room': room, 'utilization': util_dict})
    
    # Build a summary grouping rooms by average utilization.
    utilization_summary = {'high': [], 'moderate': [], 'low': []}
    for item in utilization_by_day:
        room = item['room']
        utils = list(item['utilization'].values())
        avg_util = sum(utils) / len(utils) if utils else 0
        if avg_util >= 0.8:
            utilization_summary['high'].append(room)
        elif avg_util >= 0.5:
            utilization_summary['moderate'].append(room)
        else:
            utilization_summary['low'].append(room)
    
    # Build chart data for room utilization (one dataset per day).
    rooms_sorted = sorted(room_to_util.keys())
    datasets = []
    colors = {
        'Friday': '#007bff',      # Blue
        'Monday': '#28a745',      # Green
        'Tuesday': '#ffc107',     # Yellow
        'Wednesday': '#17a2b8',   # Teal
        'Thursday': '#dc3545'     # Red
    }
    for day in days_order:
        data = []
        for room in rooms_sorted:
            data.append(room_to_util.get(room, {}).get(day, 0))
        datasets.append({
            'label': day,
            'data': data,
            'backgroundColor': colors.get(day, '#6c757d')
        })
    room_util_chart_data = {
        'labels': rooms_sorted,
        'datasets': datasets
    }
    
    # Step 3: Compute overall score and grade.
    total_score, grade = grade_schedule(room_conflicts, lecturer_conflicts, utilization, load)
    
    # Step 4: Anomaly detection (e.g., overworked lecturers).
    anomalies = perform_anomaly_detection(load)
    
    # Step 5: Generate the analysis report using NLG (including conflict details).
    report = generate_analysis_report(total_score, grade, room_conflicts, lecturer_conflicts,
                                      utilization, load, room_conflict_details, lecturer_conflict_details)
    
    # Step 6: Generate visualizations (charts).
    room_util_img, lecturer_load_img = create_visualizations(utilization, load)
    
    # Render the analysis dashboard template, passing all computed variables.
    return render_template("analysis_dashboard.html",
                           report=report,
                           grade=grade,
                           total_score=total_score,
                           room_util_img=room_util_img,
                           lecturer_load_img=lecturer_load_img,
                           anomalies=anomalies.to_dict(orient="records"),
                           room_conflict_details=room_conflict_details,
                           lecturer_conflict_details=lecturer_conflict_details,
                           utilization_by_day=utilization_by_day,
                           utilization_summary=utilization_summary,
                           room_util_chart_data=room_util_chart_data,
                           lecturer_load_groups=lecturer_load_groups,
                           lecturer_load_table=lecturer_load_table,
                           lecturer_load_pie_data=lecturer_load_pie_data)

@app.route('/start_review', methods=['POST'])
def start_review():
    """
    Populates UpdatedSessionSchedule with data from SessionSchedule.
    This route is triggered by a "Start Review" button so that
    the staging table is initialized with the live timetable.
    """
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for('conflict_free_matrix'))
    try:
        with conn.cursor() as cursor:
            # Clear the staging table
            cursor.execute("DELETE FROM UpdatedSessionSchedule")
            # Copy rows from SessionSchedule into UpdatedSessionSchedule
            cursor.execute("INSERT INTO UpdatedSessionSchedule SELECT * FROM SessionSchedule")
            conn.commit()
            flash("Review started: Timetable copied to staging area.", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Database error: {err}", "danger")
    finally:
        conn.close()
    return redirect(url_for('conflict_free_matrix'))


@app.route('/export_csv', methods=['GET', 'POST'])
def export_csv():
    if request.method == 'POST':
        title = request.form.get('title')
        semester = request.form.get('semester')  # e.g., "Semester 2"
        if not title or not semester:
            flash("Please provide a title and select a semester.", "warning")
            return redirect(url_for('export_csv'))
        
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for('export_csv'))
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Join data from UpdatedSessionSchedule, SessionAssignments, and Course
                sql = """
                    SELECT 
                        us.DayOfWeek AS Day,
                        sa.SessionType AS `Period Name`,
                        DATE_FORMAT(us.StartTime, '%H:%i') AS `From Time`,
                        DATE_FORMAT(us.EndTime, '%H:%i') AS `To Time`,
                        us.RoomName AS Location,
                        CONCAT(sa.CourseCode, ' - ', c.CourseName) AS `Course Code - Course Name`,
                        sa.LecturerName AS `Staff Code - Staff Name`,
                        sa.AdditionalStaff AS `Additional Staff`,
                        sa.CohortName AS Section,
                        %s AS `Semester/Year`,
                        sa.NumberOfEnrollments AS `Number of Enrollments`
                    FROM UpdatedSessionSchedule us
                    JOIN SessionAssignments sa ON us.SessionID = sa.SessionID
                    JOIN Course c ON sa.CourseCode = c.CourseCode
                    ORDER BY us.DayOfWeek, us.StartTime
                """
                cursor.execute(sql, (semester,))
                rows = cursor.fetchall()
        except mysql.connector.Error as err:
            flash("Error fetching data: " + str(err), "danger")
            return redirect(url_for('export_csv'))
        finally:
            conn.close()
        
        # Use the csv module to write each field into its own column
        import csv, io
        output = io.StringIO()
        fieldnames = [
            "Day",
            "Period Name",
            "From Time",
            "To Time",
            "Location",
            "Course Code - Course Name",
            "Staff Code - Staff Name",
            "Additional Staff",
            "Section",
            "Semester/Year",
            "Number of Enrollments"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        csv_content = output.getvalue()
        output.close()

        from flask import Response
        filename = f"{title.replace(' ', '_')}.csv"
        response = Response(csv_content, mimetype="text/csv")
        response.headers.set("Content-Disposition", "attachment", filename=filename)
        return response

    return render_template('export_csv.html')


@app.route('/')
def index():
    return redirect(url_for('homepage')) 

# ----------------------------------------------------
# Main
# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)