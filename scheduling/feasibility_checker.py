#!/usr/bin/env python3
"""
feasibility_checker.py

This module generates all possible non‐conflicting timetables for a student based on their
selected courses (as stored in StudentCourseSelection). For each student (identified by
(StudentID, Type)), we:
  1. Retrieve the list of courses the student selected.
  2. For each course, if the course is an elective placeholder (ELECTIVE, ELECTIVE1, or ELECTIVE2),
     expand it into the list of actual elective course codes (retrieved from the Course table
     and filtered by the student’s major via major_prefix_mapping). Then, for each course code
     (either from the original selection or from expansion), fetch available sections (cohorts)
     along with their sessions from SessionAssignments joined with UpdatedSessionSchedule .
  3. Generate every combination (Cartesian product) of one section per course.
  4. Check for time conflicts among the sessions in each combination.
  5. Return the feasible (conflict‑free) timetables (and, for debugging, also those with conflicts).

A Flask blueprint (feasibility_bp) is provided to expose the results as a JSON endpoint.
"""

import mysql.connector
import logging
from datetime import datetime, timedelta
from itertools import product
from collections import defaultdict
from flask import Blueprint, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Database Connection Helper
# ---------------------------
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

# ---------------------------
# Major Prefix Mapping (Unused without electives)
# ---------------------------
major_prefix_mapping = {
    1: ['BUSA', 'ECON'],       # Business Administration
    2: ['CS'],                 # Computer Science
    3: ['IS', 'MIS', 'CS'],    # Management Information Systems
    4: ['CE', 'ENGR', 'CS'],   # Computer Engineering
    5: ['MECH'],               # Mechatronics Engineering (assumed)
    6: ['ME', 'ENGR'],         # Mechanical Engineering
    7: ['EE', 'ENGR'],         # Electrical and Electronic Engineering
    8: ['LAW'],                # Law with Public Policy (assumed)
}

def get_student_major_prefixes(student_id):
    """
    Retrieves the student's MajorID from the Student table and returns the associated
    list of elective prefixes.
    (This function is retained for use when expanding electives.)
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT MajorID FROM Student WHERE StudentID = %s", (student_id,))
            row = cursor.fetchone()
            if row and row.get("MajorID"):
                major_id = row["MajorID"]
                return major_prefix_mapping.get(major_id, [])
            else:
                return []
    except Exception as e:
        logging.error(f"Error retrieving major for student {student_id}: {e}")
        return []
    finally:
        conn.close()

# ------------------------------------------------
# Helper: Fetch All Real Elective Courses
# ------------------------------------------------
def fetch_all_electives_codes():
    """
    Retrieves a list of CourseCodes for all real elective courses.
    Excludes the placeholder codes (ELECTIVE, ELECTIVE1, ELECTIVE2).
    """
    codes = []
    conn = get_db_connection()
    if not conn:
        return codes
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT CourseCode 
                FROM Course 
                WHERE RequirementType = 'Elective'
                  AND CourseCode NOT IN ('ELECTIVE', 'ELECTIVE1', 'ELECTIVE2')
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            codes = [row["CourseCode"] for row in rows]
    except Exception as e:
        logging.error(f"Error fetching elective courses: {e}")
    finally:
        conn.close()
    return codes

# ------------------------------------------------
# Helper: Expand Elective Placeholders
# ------------------------------------------------
def expand_electives(course_code, student_id):
    """
    If course_code is one of the placeholders ("ELECTIVE", "ELECTIVE1", "ELECTIVE2"),
    retrieve the corresponding list of real elective course codes.
    Otherwise, return a list with the original course_code.
    """
    if course_code not in ("ELECTIVE", "ELECTIVE1", "ELECTIVE2"):
        return [course_code]
    
    elective_codes = fetch_all_electives_codes()
    if course_code == "ELECTIVE":
        return elective_codes
    prefixes = get_student_major_prefixes(student_id)
    if course_code == "ELECTIVE1":
        # Major electives: only those elective courses whose code starts with a major prefix.
        return [c for c in elective_codes if any(c.startswith(prefix) for prefix in prefixes)]
    if course_code == "ELECTIVE2":
        # Non-major electives: electives that do not match any of the major prefixes.
        return [c for c in elective_codes if not any(c.startswith(prefix) for prefix in prefixes)]
    return [course_code]  # Fallback

# ------------------------------------------------
# Fetch Available Sections for a Given Course
# ------------------------------------------------
def fetch_sections_for_course(course_code):
    """
    For a given course code, fetch available sections (cohorts)
    and their sessions from SessionAssignments joined with UpdatedSessionSchedule .
    Returns a list of section dictionaries.
    """
    sections = defaultdict(list)
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT sa.CohortName, ss.DayOfWeek, ss.StartTime, ss.EndTime
                FROM SessionAssignments sa
                JOIN UpdatedSessionSchedule  ss ON sa.SessionID = ss.SessionID
                WHERE sa.CourseCode = %s
            """
            cursor.execute(query, (course_code,))
            rows = cursor.fetchall()
            for row in rows:
                cohort = row["CohortName"]
                session_info = {
                    "day": row["DayOfWeek"],
                    "start": row["StartTime"],
                    "end": row["EndTime"]
                }
                sections[cohort].append(session_info)
    except Exception as e:
        logging.error(f"Error fetching sections for course {course_code}: {e}")
    finally:
        conn.close()
    section_list = []
    for cohort, sessions in sections.items():
        if sessions:  # Only include sections with at least one session.
            section_list.append({
                "cohort": cohort,
                "sessions": sessions,
                "course_code": course_code
            })
    return section_list

# ------------------------------------------------
# Check if Two Sessions Overlap (Conflict Checker)
# ------------------------------------------------
def sessions_conflict(s1, s2):
    """
    Given two sessions (each with keys: day, start, end),
    returns True if they overlap in time (on the same day).
    """
    if s1["day"] != s2["day"]:
        return False
    return s1["start"] < s2["end"] and s1["end"] > s2["start"]

# ------------------------------------------------
# Check if a Combination of Sections has any Conflicts
# ------------------------------------------------
def timetable_conflicts(section_combination):
    """
    Given a list of sections (each as a dict with its sessions),
    check for any time conflicts among all sessions.
    Each section’s sessions are treated as an atomic block.
    """
    all_sessions = []
    for sec in section_combination:
        if not sec.get("sessions"):
            continue
        all_sessions.extend(sec["sessions"])
    n = len(all_sessions)
    for i in range(n):
        for j in range(i + 1, n):
            if sessions_conflict(all_sessions[i], all_sessions[j]):
                return True
    return False

# ------------------------------------------------
# (Optional) Iterative Combination Builder
# ------------------------------------------------
def generate_timetables_iterative(sections_by_course):
    """
    An alternative to a full Cartesian product: iteratively build the timetable.
    """
    feasible = []
    base_candidates = sections_by_course[0]
    for sec in base_candidates:
        candidate = [sec]
        def add_section(index, current_candidate):
            if index >= len(sections_by_course):
                feasible.append(current_candidate)
                return
            for sec in sections_by_course[index]:
                new_candidate = current_candidate + [sec]
                if not timetable_conflicts(new_candidate):
                    add_section(index + 1, new_candidate)
        add_section(1, candidate)
    return feasible

# ------------------------------------------------
# Generate Feasible Timetables for a Single Student
# ------------------------------------------------
def generate_feasible_timetables_for_student(course_codes, student_id):
    """
    Given a list of course codes for a student and the student's ID,
    fetch sections for each course (expanding electives as needed),
    then generate and filter combinations based on time conflicts.

    Returns a tuple: (feasible_combinations, conflicting_combinations)
    """
    # Expand elective placeholders:
    # For each course code, if it is ELECTIVE/ELECTIVE1/ELECTIVE2, expand it to a list of real elective codes.
    expanded_course_list = []
    for code in course_codes:
        expanded = expand_electives(code, student_id)
        expanded_course_list.append(expanded)
    
    # For each group (list of course codes) in the expanded list, fetch all sections and merge them.
    sections_by_course = []
    for group in expanded_course_list:
        group_sections = []
        for code in group:
            secs = fetch_sections_for_course(code)
            if secs:
                group_sections.extend(secs)
        if not group_sections:
            logging.warning(f"No sections found for course group {group}.")
            sections_by_course = []
            break
        sections_by_course.append(group_sections)
    
    overall_feasible = []
    overall_conflicts = []
    if not sections_by_course:
        return overall_feasible, overall_conflicts
    # Full Cartesian product approach:
    for combination in product(*sections_by_course):
        if timetable_conflicts(combination):
            overall_conflicts.append(combination)
        else:
            overall_feasible.append(combination)
    # Alternatively, one could use the iterative approach:
    # feasible_iter = generate_timetables_iterative(sections_by_course)
    # overall_feasible.extend(feasible_iter)
    return overall_feasible, overall_conflicts

# ------------------------------------------------
# Fetch Student Course Selections from Database
# ------------------------------------------------
def fetch_student_course_selections():
    """
    Returns a dictionary with keys as (StudentID, Type)
    and values as lists of CourseCodes selected.
    """
    selections = defaultdict(list)
    conn = get_db_connection()
    if not conn:
        return selections
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT StudentID, CourseCode, Type FROM StudentCourseSelection")
            rows = cursor.fetchall()
            for row in rows:
                key = (row["StudentID"], row["Type"])
                selections[key].append(row["CourseCode"])
    except Exception as e:
        logging.error("Error fetching student course selections: " + str(e))
    finally:
        conn.close()
    return selections

# ------------------------------------------------
# Generate Timetables for All Students in the System
# ------------------------------------------------
def generate_all_feasible_timetables_with_conflicts():
    """
    For each unique student (identified by (StudentID, Type) in StudentCourseSelection),
    generate all feasible timetables based on the courses selected.

    Returns a dictionary mapping (StudentID, Type) to a dict with keys:
       "courses", "feasible_timetables", "conflict_timetables"
    """
    results = {}
    selections = fetch_student_course_selections()  # key: (StudentID, Type)
    for key, course_list in selections.items():
        student_id, sel_type = key
        feasible, conflicts = generate_feasible_timetables_for_student(course_list, student_id)
        results[key] = {
            "courses": course_list,
            "feasible_timetables": feasible,
            "conflict_timetables": conflicts
        }
    return results

# ------------------------------------------------
# Flask Blueprint for Feasibility Check Endpoint
# ------------------------------------------------
feasibility_bp = Blueprint('feasibility', __name__)

@feasibility_bp.route('/feasibility_check', methods=['GET'])
def feasibility_check():
    """
    Flask endpoint that returns the feasibility check results as JSON.
    For each student (StudentID and Type) it returns the list of courses selected and
    the feasible timetables found (with sessions’ times formatted as "HH:MM").
    """
    try:
        results = generate_all_feasible_timetables_with_conflicts()
        serializable_results = {}
        for key, data in results.items():
            student_id, sel_type = key
            feasibles_serial = []
            for combo in data["feasible_timetables"]:
                combo_serial = []
                for sec in combo:
                    sec_serial = {
                        "cohort": sec["cohort"],
                        "course_code": sec["course_code"],
                        "sessions": []
                    }
                    for s in sec["sessions"]:
                        start_str = s["start"].strftime("%H:%M") if hasattr(s["start"], "strftime") else str(s["start"])
                        end_str = s["end"].strftime("%H:%M") if hasattr(s["end"], "strftime") else str(s["end"])
                        sec_serial["sessions"].append({
                            "day": s["day"],
                            "start": start_str,
                            "end": end_str
                        })
                    combo_serial.append(sec_serial)
                feasibles_serial.append(combo_serial)
            serializable_results[f"{student_id}_{sel_type}"] = {
                "courses": data["courses"],
                "feasible_timetables": feasibles_serial,
                "conflict_timetables_count": len(data["conflict_timetables"])
            }
        return jsonify(serializable_results), 200
    except Exception as e:
        logging.error("Error in feasibility check endpoint: " + str(e))
        return jsonify({"message": "Error during feasibility check", "error": str(e)}), 500

if __name__ == '__main__':
    # To run the feasibility checker standalone, create a minimal Flask app.
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(feasibility_bp, url_prefix='/')
    app.run(debug=True)