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
     along with their sessions from SessionAssignments joined with UpdatedSessionSchedule.
  3. Generate every combination (Cartesian product) of one section per course.
  4. Check for time conflicts among the sessions in each combination.
  5. Return the feasible (conflict‑free) timetables (and, for debugging, also those with conflicts).

A Flask blueprint (feasibility_bp) is provided to expose the results as a JSON endpoint.
"""

from curses import flash
import sys
import mysql.connector
import logging
import json  # <-- For dumping the final JSON
from datetime import datetime, timedelta
from itertools import product
from collections import defaultdict
from flask import Blueprint, jsonify, render_template
import pygad
import random

# ------------------------------------------------------------------------------
# Configure Logging to write both to stdout and to a file called "app.log"
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

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
            cursor.execute(query, ())
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
    and their sessions from SessionAssignments joined with UpdatedSessionSchedule.
    Returns a list of section dictionaries.
    """
    from collections import defaultdict
    sections = defaultdict(list)
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT sa.CohortName, ss.DayOfWeek, ss.StartTime, ss.EndTime
                FROM SessionAssignments sa
                JOIN UpdatedSessionSchedule ss ON sa.SessionID = ss.SessionID
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
# Utility: Parse Time Strings
# ------------------------------------------------
def parse_time(time_val):
    """
    Convert time_val to a time object.
    Handles time objects, strings in "HH:MM:SS" or "HH:MM" format, or timedelta.
    """
    from datetime import datetime, timedelta
    if isinstance(time_val, timedelta):
        # Convert timedelta to time by adding it to datetime.min.
        return (datetime.min + time_val).time()
    if hasattr(time_val, 'strftime'):
        return time_val
    try:
        return datetime.strptime(time_val, "%H:%M:%S").time()
    except ValueError:
        return datetime.strptime(time_val, "%H:%M").time()

# ------------------------------------------------
# Utility: Check if Two Sessions Conflict
# ------------------------------------------------
def sessions_conflict(s1, s2):
    """
    Given two sessions (each with keys: day, start, end),
    returns True if they overlap on the same day.
    Convert times to time objects for reliable comparisons.
    """
    day1 = s1["day"].strip()
    day2 = s2["day"].strip()
    if day1 != day2:
        return False

    start1 = parse_time(s1["start"])
    end1   = parse_time(s1["end"])
    start2 = parse_time(s2["start"])
    end2   = parse_time(s2["end"])
    
    # Log the comparison for diagnostics
    logging.info("Comparing %s %s–%s vs %s %s–%s",
                 day1, start1, end1, day2, start2, end2)
    
    return start1 < end2 and end1 > start2

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
def generate_feasible_timetables_for_student(course_codes, student_id, max_combinations=500):
    """
    Given a list of course codes for a student and the student's ID,
    fetch sections for each course (expanding electives as needed),
    then generate and filter combinations based on time conflicts.
    
    A maximum of 'max_combinations' total timetable combinations (feasible + conflict)
    will be generated to prevent combinatorial explosion.
    
    Returns a tuple: (feasible_combinations, conflicting_combinations)
    """
    # Expand elective placeholders:
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
    
    # Full Cartesian product approach with a limit
    from itertools import product
    for combination in product(*sections_by_course):
        # Check the total count of combinations so far
        if len(overall_feasible) + len(overall_conflicts) >= max_combinations:
            logging.info("Reached the maximum combination limit (%s).", max_combinations)
            break
        if timetable_conflicts(combination):
            overall_conflicts.append(combination)
        else:
            overall_feasible.append(combination)
    
    return overall_feasible, overall_conflicts

# ------------------------------------------------
# Fetch Student Course Selections from Database
# ------------------------------------------------
def fetch_student_course_selections():
    """
    Returns a dictionary with keys as (StudentID, Type)
    and values as lists of CourseCodes selected.
    """
    from collections import defaultdict
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
# Updated: Compute Conflict Flags for a Timetable Combination
# ------------------------------------------------
def get_conflict_flags(section_combination):
    """
    Given a combination (list of sections, each with a list of sessions),
    returns a list of lists (one per section) of booleans indicating whether
    each session is involved in any conflict.

    This version checks for conflicts both within the same section
    (intra‐section) and across different sections (inter‐section).
    """
    conflict_flags = []
    converted = []
    
    # Pre-convert session times for each section.
    for sec in section_combination:
        session_times = []
        for s in sec.get("sessions", []):
            day = s["day"].strip()
            session_times.append({
                "day": day,
                "start": parse_time(s["start"]),
                "end": parse_time(s["end"])
            })
        converted.append(session_times)
        conflict_flags.append([False] * len(session_times))
    
    # Check for conflicts within the same section
    for i, sessions in enumerate(converted):
        for a in range(len(sessions)):
            for b in range(a + 1, len(sessions)):
                if sessions[a]["day"] == sessions[b]["day"]:
                    if sessions[a]["start"] < sessions[b]["end"] and sessions[a]["end"] > sessions[b]["start"]:
                        conflict_flags[i][a] = True
                        conflict_flags[i][b] = True
    
    # Check for conflicts across different sections
    n_sections = len(converted)
    for i in range(n_sections):
        for a in range(len(converted[i])):
            for j in range(i + 1, n_sections):
                for b in range(len(converted[j])):
                    if converted[i][a]["day"] == converted[j][b]["day"]:
                        if (converted[i][a]["start"] < converted[j][b]["end"] and
                            converted[i][a]["end"] > converted[j][b]["start"]):
                            conflict_flags[i][a] = True
                            conflict_flags[j][b] = True
    return conflict_flags

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

def run_feasibility_check_background():
    """
    Runs the heavy feasibility check in the background and emits an update event
    via SocketIO when complete.
    """
    try:
        results = generate_all_feasible_timetables_with_conflicts()
        logging.info("Background feasibility check completed successfully.")
        # Import the SocketIO instance from your app
        from app import socketio
        # Emit an event to all clients on the default namespace
        socketio.emit('update_feasibility', {'data': results}, namespace='/')
    except Exception as e:
        logging.error("Error in background feasibility check: " + str(e))

# ------------------------------------------------
# Flask Blueprint for Feasibility Check Endpoint
# ------------------------------------------------
feasibility_bp = Blueprint('feasibility', __name__)

@feasibility_bp.route('/feasibility_check', methods=['GET'])
def feasibility_check():
    logging.info("Entered feasibility_check endpoint with GA optimization.")
    try:
        # Use the GA-based feasibility checker
        results = genetic_algorithm_feasibility_check()
        serializable_results = {}

        for key, data in results.items():
            student_id, sel_type = key
            student_key = f"{student_id}_{sel_type}"
            feasibles_serial = []
            # Serialize feasible timetables (all sessions marked conflict: False)
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
                            "end": end_str,
                            "conflict": False
                        })
                    combo_serial.append(sec_serial)
                feasibles_serial.append(combo_serial)
            
            # Process conflict timetables similarly
            conflicts_serial = []
            logging.info("Student %s: conflict_timetables length = %s", student_key, len(data["conflict_timetables"]))
            for combo in data["conflict_timetables"]:
                flags = get_conflict_flags(combo)
                logging.info("Computed conflict flags for student %s: %s", student_key, flags)
                
                # Extra check: log a warning if no session in the combination is flagged.
                if all(all(flag == False for flag in section_flags) for section_flags in flags):
                    logging.warning("Conflict combination for student %s flagged at course level, but no session-level overlaps detected.", student_key)
                
                combo_serial = []
                for idx, sec in enumerate(combo):
                    sec_serial = {
                        "cohort": sec["cohort"],
                        "course_code": sec["course_code"],
                        "sessions": []
                    }
                    for s, flag in zip(sec["sessions"], flags[idx]):
                        start_str = s["start"].strftime("%H:%M") if hasattr(s["start"], "strftime") else str(s["start"])
                        end_str = s["end"].strftime("%H:%M") if hasattr(s["end"], "strftime") else str(s["end"])
                        sec_serial["sessions"].append({
                            "day": s["day"],
                            "start": start_str,
                            "end": end_str,
                            "conflict": flag
                        })
                    combo_serial.append(sec_serial)
                conflicts_serial.append(combo_serial)
            logging.info("Serialized conflict timetables for student %s: %s", student_key, conflicts_serial)
            
            serializable_results[student_key] = {
                "courses": data["courses"],
                "feasible_timetables": feasibles_serial,
                "conflict_timetables": conflicts_serial,
                "conflict_timetables_count": len(conflicts_serial)
            }
        
        logging.info("Final serialized results (dict): %s", serializable_results)
        for handler in logging.getLogger().handlers:
            handler.flush()
        return render_template('feasibility_check.html', feasibility_results=serializable_results)
    except Exception as e:
        logging.error("Error in feasibility check endpoint: " + str(e))
        flash("Error during feasibility check: " + str(e), "danger")
        return render_template("feasibility_check.html", feasibility_results={})
    

def count_conflicts(timetable):
    """
    Given a candidate timetable (a list of section dicts, each with a 'sessions' list),
    count the number of conflicting session pairs.
    """
    all_sessions = []
    for sec in timetable:
        all_sessions.extend(sec.get("sessions", []))
    conflict = 0
    n = len(all_sessions)
    for i in range(n):
        for j in range(i+1, n):
            if sessions_conflict(all_sessions[i], all_sessions[j]):
                conflict += 1
    return conflict

def genetic_algorithm_feasibility_check(max_generations=100, population_size=150):
    """
    Uses a genetic algorithm to generate timetable combinations per student.
    Returns a dict similar to generate_all_feasible_timetables_with_conflicts().
    """
    results = {}
    selections = fetch_student_course_selections()  # keys: (StudentID, Type)
    for key, course_list in selections.items():
        student_id, sel_type = key
        student_key = f"{student_id}_{sel_type}"
        
        # Expand elective placeholders and fetch available sections for each course.
        sections_by_course = []
        for code in course_list:
            expanded = expand_electives(code, student_id)
            group_sections = []
            for ec in expanded:
                secs = fetch_sections_for_course(ec)
                if secs:
                    group_sections.extend(secs)
            if not group_sections:
                logging.warning(f"No sections found for course group {expanded} for student {student_id}.")
                sections_by_course = []
                break
            sections_by_course.append(group_sections)
        
        if not sections_by_course:
            results[key] = {"courses": course_list, "feasible_timetables": [], "conflict_timetables": [], "conflict_timetables_count": 0}
            continue

        num_courses = len(sections_by_course)

        # Updated fitness function accepting three parameters.
        def fitness_func(ga_instance, solution, solution_idx):
            candidate = []
            for i in range(num_courses):
                idx = int(solution[i])
                candidate.append(sections_by_course[i][idx])
            conflict_count = count_conflicts(candidate)
            return 1.0 / (1.0 + conflict_count)

        # For each gene (course), the gene space is the list of valid indices.
        gene_space = [list(range(len(group))) for group in sections_by_course]

        ga_instance = pygad.GA(
            num_generations=max_generations,
            num_parents_mating=10,
            fitness_func=fitness_func,
            sol_per_pop=population_size,
            num_genes=num_courses,
            gene_space=gene_space,
            mutation_percent_genes=10,
            mutation_type="random",
            stop_criteria=["saturate_10"]
        )
        ga_instance.run()

        # Evaluate the final population.
        feasible_timetables = []
        conflict_timetables = []
        for sol in ga_instance.population:
            candidate = []
            for i in range(num_courses):
                idx = int(sol[i])
                candidate.append(sections_by_course[i][idx])
            if count_conflicts(candidate) == 0:
                feasible_timetables.append(candidate)
            else:
                conflict_timetables.append(candidate)

        results[key] = {
            "courses": course_list,
            "feasible_timetables": feasible_timetables,
            "conflict_timetables": conflict_timetables,
            "conflict_timetables_count": len(conflict_timetables)
        }
    return results

# ------------------------------------------------
# Run the Feasibility Checker as a Standalone Flask App
# ------------------------------------------------
if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(feasibility_bp, url_prefix='/')
    app.run(debug=True)