import datetime
import mysql.connector
import logging
from datetime import time, timedelta, datetime
from collections import defaultdict
from flask import Flask, request, render_template, flash, redirect
from flask import Blueprint

app = Flask(__name__)
feasibility_bp = Blueprint('feasibility', __name__)

# ----------------------------------------------------------------
# Helper functions to get data from the database.
# ----------------------------------------------------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Naakey057@",
            database="schedulai"
        )
        return conn
    except mysql.connector.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

def fetch_student_course_selections():
    """
    Fetches rows from StudentCourseSelection.
    Expected columns: StudentID, CourseCode, Type
    """
    query = "SELECT StudentID, CourseCode, Type FROM StudentCourseSelection"
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        selections = cursor.fetchall()
        return selections
    except mysql.connector.Error as err:
        logging.error(f"Error fetching course selections: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_final_schedule():
    query = """
        SELECT sa.CourseCode, sa.CohortName, ss.DayOfWeek, ss.StartTime, ss.EndTime
        FROM SessionAssignments sa
        JOIN SessionSchedule ss ON sa.SessionID = ss.SessionID
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        logging.error(f"Error fetching final schedule: {err}")
        return []

def fetch_students():
    """
    Fetches basic student information.
    Expected columns include: StudentID, YearNumber, MajorID, etc.
    """
    query = "SELECT StudentID, YearNumber, MajorID FROM Student"
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        logging.error(f"Error fetching students: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# ----------------------------------------------------------------
# Helper to determine if two time intervals overlap.
# ----------------------------------------------------------------
def times_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
    """Return True if the two time intervals overlap."""
    return max(start1, start2) < min(end1, end2)

# ----------------------------------------------------------------
# Updated feasibility check function
# This function now groups the course selections by (StudentID, Type)
# and then, for each group, attempts to assign a cohort for each course
# such that none of the chosen sessions overlap.
# ----------------------------------------------------------------
def run_feasibility_check() -> list:
    """
    Checks feasibility for student course selections by grouping them by 
    (StudentID, Type) so that scheduling conflicts are resolved within each group.
    
    Returns a list of conflict dicts (if any).
    """
    try:
        selections = fetch_student_course_selections()
        students = fetch_students()
        final_schedule = fetch_final_schedule()
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return [{"Error": "Data fetching failed"}]
    
    # Group course selections by (StudentID, Type)
    student_groups = defaultdict(list)
    for sel in selections:
        # Skip elective courses (from ProgramPlan) with course codes ELECTIVE1 or ELECTIVE2.
        if sel['CourseCode'] in ('ELECTIVE1', 'ELECTIVE2'):
            continue
        group_key = (sel['StudentID'], sel.get('Type') or 'No Subtype')
        student_groups[group_key].append(sel['CourseCode'])
    
    # Organize the available sessions by (CourseCode, CohortName)
    sessions_by_course_cohort = defaultdict(list)
    for sess in final_schedule:
        key = (sess["CourseCode"], sess["CohortName"])
        sessions_by_course_cohort[key].append(sess)
    
    conflicts = []
    
    # For each (student, type) group, try to assign a cohort per course.
    for (student_id, type_), courses in student_groups.items():
        # Get a simple student label for reporting.
        student_info = next((s for s in students if s["StudentID"] == student_id), {})
        student_label = f"StudentID {student_id} ({type_})"
        
        # For each course, build a list of available cohorts.
        available_cohorts = {}
        for course in courses:
            cohorts = {key[1] for key in sessions_by_course_cohort if key[0] == course}
            if not cohorts:
                conflicts.append({
                    "Student": student_label,
                    "Conflict": f"No available cohorts for course {course}"
                })
                break  # Skip further processing for this group
            available_cohorts[course] = list(cohorts)
        else:
            # Backtracking assignment: try to choose one cohort per course
            assigned = {}
            session_assignments = []  # List of sessions (from chosen cohorts) for this student group
            
            def backtrack(i):
                if i == len(courses):
                    return True  # All courses have been assigned a feasible cohort
                course = courses[i]
                for cohort in available_cohorts[course]:
                    sessions = sessions_by_course_cohort.get((course, cohort), [])
                    conflict_found = False
                    # Check for conflicts with sessions already assigned in this group.
                    for sess in sessions:
                        for assigned_sess in session_assignments:
                            if sess["DayOfWeek"] == assigned_sess["DayOfWeek"]:
                                if times_overlap(sess["StartTime"], sess["EndTime"],
                                                 assigned_sess["StartTime"], assigned_sess["EndTime"]):
                                    conflict_found = True
                                    break
                        if conflict_found:
                            break
                    if conflict_found:
                        continue
                    # Assign this cohort and add its sessions.
                    assigned[course] = cohort
                    session_assignments.extend(sessions)
                    if backtrack(i + 1):
                        return True
                    # Backtrack: remove the sessions for this course.
                    for _ in sessions:
                        session_assignments.pop()
                    assigned.pop(course, None)
                return False
            
            if not backtrack(0):
                conflicts.append({
                    "Student": student_label,
                    "Conflict": "No feasible cohort assignments found without scheduling conflicts."
                })
    return conflicts

# ----------------------------------------------------------------
# Helper: Generate list of timeslots (e.g. every 30 minutes)
# ----------------------------------------------------------------
def generate_timeslots(start="08:00", end="19:00", interval_minutes=30):
    timeslots = []
    start_dt = datetime.strptime(start, "%H:%M")
    end_dt = datetime.strptime(end, "%H:%M")
    current = start_dt
    while current <= end_dt:
        timeslots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=interval_minutes)
    return timeslots

# ----------------------------------------------------------------
# NEW ROUTE: /timetable_combinations
# This route reads query parameters (student_id and type), uses a backtracking
# routine to generate all conflict-free timetable combinations for the student's
# course selections, and prepares grid parameters for display.
# ----------------------------------------------------------------
@feasibility_bp.route('/timetable_combinations')
def timetable_combinations():
    student_id = request.args.get("student_id", type=int)
    course_type = request.args.get("type", default="No Subtype")
    if not student_id:
        flash("Student ID missing", "danger")
        return redirect("/")
    
    # Fetch the student's courses for the specified type.
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Exclude courses ELECTIVE1 and ELECTIVE2 from the student's course selections.
            query = """
                SELECT CourseCode 
                FROM StudentCourseSelection 
                WHERE StudentID = %s 
                  AND Type = %s 
                  AND CourseCode NOT IN ('ELECTIVE1', 'ELECTIVE2')
            """
            cursor.execute(query, (student_id, course_type))
            rows = cursor.fetchall()
        courses = [r["CourseCode"] for r in rows]
    except Exception as e:
        logging.error(f"Error fetching courses for student {student_id}: {e}")
        courses = []
    finally:
        conn.close()
    
    if not courses:
        flash("No courses found for the selected student and type.", "warning")
        return redirect("/")
    
    # Fetch final schedule sessions.
    final_schedule = fetch_final_schedule()
    
    # Organize available sessions by (CourseCode, CohortName)
    sessions_by_course_cohort = defaultdict(list)
    for sess in final_schedule:
        key = (sess["CourseCode"], sess["CohortName"])
        sessions_by_course_cohort[key].append(sess)
    
    # Determine available cohorts for each course.
    available_cohorts = {}
    for course in courses:
        cohorts = {key[1] for key in sessions_by_course_cohort if key[0] == course}
        if not cohorts:
            flash(f"No available cohorts for course {course}", "danger")
            available_cohorts[course] = []
        else:
            available_cohorts[course] = list(cohorts)
    
    # Backtracking: generate all conflict-free combinations.
    solutions = []  # Each solution is a tuple: (assignment, session_list)
    current_assignment = {}
    current_sessions = []  # List of session dicts

    def backtrack(i):
        if i == len(courses):
            solutions.append((current_assignment.copy(), list(current_sessions)))
            return
        course = courses[i]
        for cohort in available_cohorts[course]:
            sessions = sessions_by_course_cohort.get((course, cohort), [])
            conflict_found = False
            for sess in sessions:
                for assigned_sess in current_sessions:
                    if sess["DayOfWeek"] == assigned_sess["DayOfWeek"]:
                        if times_overlap(sess["StartTime"], sess["EndTime"],
                                         assigned_sess["StartTime"], assigned_sess["EndTime"]):
                            conflict_found = True
                            break
                if conflict_found:
                    break
            if conflict_found:
                continue
            current_assignment[course] = cohort
            num_added = len(sessions)
            current_sessions.extend(sessions)
            backtrack(i+1)
            for _ in range(num_added):
                current_sessions.pop()
            current_assignment.pop(course, None)
    
    backtrack(0)
    logging.info(f"Generated {len(solutions)} conflict-free timetable combinations for student {student_id} ({course_type}).")
    
    # Define grid parameters.
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    timeslots = generate_timeslots("08:00", "19:00", 30)
    
    return render_template("timetable_combinations.html",
                           solutions=solutions,
                           student_id=student_id,
                           type=course_type,
                           days=days,
                           timeslots=timeslots)

# ----------------------------------------------------------------
# For testing purposes you might run this module directly.
# ----------------------------------------------------------------
if __name__ == "__main__":
    conflict_list = run_feasibility_check()
    if conflict_list:
        print("Conflicts detected:")
        for c in conflict_list:
            print(c)
    else:
        print("No conflicts detected. All course selections are feasible.")