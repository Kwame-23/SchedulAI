# feasibility_checker.py

import mysql.connector
from datetime import time
from collections import defaultdict
import json
import logging
import os
import argparse

def get_db_connection():
    """
    Returns a MySQL connection object to the 'schedulai' database.
    Credentials are fetched from environment variables for security.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'schedulai')
        )
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to the database: {err}")
        raise

def fetch_final_schedule():
    """
    Joins SessionAssignments + SessionSchedule to get day/time for each session.
    Returns a list of dicts with session details.
    """
    query = """
        SELECT sa.SessionID,
               sa.CourseCode,
               sa.CohortName,
               sa.SessionType,
               sa.Duration,
               sa.NumberOfEnrollments,
               ss.DayOfWeek,
               ss.StartTime,
               ss.EndTime,
               ss.RoomName
        FROM SessionAssignments AS sa
        JOIN SessionSchedule AS ss ON sa.SessionID = ss.SessionID
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

def fetch_student_course_selections():
    """
    Fetches all student course selections with their Types.
    Returns a list of dicts with selection details.
    """
    query = "SELECT SelectionID, StudentID, CourseCode, Type FROM StudentCourseSelection"
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                selections = cursor.fetchall()
        return selections
    except mysql.connector.Error as err:
        logging.error(f"Error fetching student course selections: {err}")
        return []

def fetch_students():
    """
    Fetches all students from the 'Student' table.
    Returns a list of dicts with student details.
    """
    query = "SELECT StudentID, MajorID, YearNumber FROM Student"
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        logging.error(f"Error fetching students: {err}")
        return []

def fetch_majors():
    """
    Fetches all majors from the 'Major' table.
    Returns a list of dicts with major details.
    """
    query = "SELECT MajorID, MajorName FROM Major"
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                majors = cursor.fetchall()
        return majors
    except mysql.connector.Error as err:
        logging.error(f"Error fetching majors: {err}")
        return []

def fetch_cohorts():
    """
    Fetches all cohorts from the 'Cohort' table.
    Returns a list of dicts with cohort details.
    """
    query = "SELECT CohortID, CohortName FROM Cohort"
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                cohorts = cursor.fetchall()
        return cohorts
    except mysql.connector.Error as err:
        logging.error(f"Error fetching cohorts: {err}")
        return []

def times_overlap(startA: time, endA: time, startB: time, endB: time) -> bool:
    """
    Determines if two time intervals overlap.
    """
    return max(startA, startB) < min(endA, endB)

def ordinal(n: int) -> str:
    """
    Converts an integer into its ordinal representation (e.g., 1 -> "1st").
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def convert_time_to_hhmm(t: time) -> str:
    """
    Converts a datetime.time object to "HH:MM" string.
    """
    if not t:
        return "N/A"
    return t.strftime("%H:%M")

def run_feasibility_check() -> list:
    """
    Main function that checks feasibility for all unique (StudentID, Type) pairs.
    Also checks for cross-type conflicts for the same student.
    Returns a list of conflict dicts.
    """
    # Fetch all necessary data
    final_schedule = fetch_final_schedule()
    students = fetch_students()
    majors = fetch_majors()
    cohorts = fetch_cohorts()
    course_selections = fetch_student_course_selections()
    
    # Create mappings
    major_map = {m['MajorID']: m['MajorName'] for m in majors}
    cohort_names = [c['CohortName'] for c in cohorts]
    
    # Organize course selections by (StudentID, Type)
    student_type_map = defaultdict(list)  # key: (StudentID, Type), value: list of CourseCodes
    for selection in course_selections:
        student_id = selection['StudentID']
        course_code = selection['CourseCode']
        type_ = selection['Type']
        if type_ and type_ != 'No Subtype':
            student_type_map[(student_id, type_)].append(course_code)
        else:
            student_type_map[(student_id, 'No Subtype')].append(course_code)
    
    # Organize sessions by CourseCode and CohortName
    sessions_by_course_cohort = defaultdict(list)  # key: (CourseCode, CohortName), value: list of sessions
    for sess in final_schedule:
        key = (sess["CourseCode"], sess["CohortName"])
        sessions_by_course_cohort[key].append(sess)
    
    # Organize all sessions by StudentID across Types
    student_sessions_map = defaultdict(list)  # key: StudentID, value: list of sessions
    
    conflicts = []
    
    # Iterate over each (StudentID, Type) pair
    for (student_id, type_), courses in student_type_map.items():
        # Fetch student's major and year
        student_info = next((stu for stu in students if stu['StudentID'] == student_id), None)
        if not student_info:
            logging.warning(f"StudentID {student_id} not found in Student table.")
            continue  # Skip if student not found
        
        major_id = student_info['MajorID']
        year_number = student_info['YearNumber']
        major_name = major_map.get(major_id, "Unknown Major")
        
        # Format student label
        if type_ and type_ != 'No Subtype':
            student_label = f"StudentID {student_id}, {ordinal(year_number)}-year {major_name}, {type_}"
        else:
            student_label = f"StudentID {student_id}, {ordinal(year_number)}-year {major_name}"
        
        logging.info(f"Processing {student_label} with courses: {courses}")
        
        # Get available cohorts for each course
        available_cohorts_per_course = {}
        for course in courses:
            cohorts_available = set()
            for sess in final_schedule:
                if sess["CourseCode"] == course:
                    cohorts_available.add(sess["CohortName"])
            available_cohorts_per_course[course] = list(cohorts_available)
        
        # Check if any course has no available cohorts
        no_cohort_courses = [course for course, cohorts in available_cohorts_per_course.items() if not cohorts]
        if no_cohort_courses:
            conflict_entry = {
                "Student": student_label,
                "Conflicts": [
                    {
                        "Type": "Cohort Assignment",
                        "Details": f"No available cohorts found for courses: {', '.join(no_cohort_courses)}."
                    }
                ]
            }
            conflicts.append(conflict_entry)
            logging.info(f"Conflict detected for {student_label}: No cohorts for courses {no_cohort_courses}.")
            continue  # Proceed to next student
        
        # Prepare to assign cohorts using backtracking
        assigned_cohorts = {}
        session_assignments = []  # List of sessions assigned to the student for this Type
        max_sessions_conflicts = []
        overlapping_conflicts = []
        
        # Sort courses by the number of available cohorts (least first) to optimize backtracking
        sorted_courses = sorted(courses, key=lambda c: len(available_cohorts_per_course[c]))
        
        def backtrack(course_index):
            if course_index == len(sorted_courses):
                return True  # All courses assigned successfully
            
            course = sorted_courses[course_index]
            for cohort in available_cohorts_per_course[course]:
                # Get sessions for this course and cohort
                sessions = sessions_by_course_cohort.get((course, cohort), [])
                
                # Check for time conflicts with already assigned sessions within this Type
                conflict_found = False
                for sess in sessions:
                    for assigned_sess in session_assignments:
                        if sess["DayOfWeek"] != assigned_sess["DayOfWeek"]:
                            continue
                        if times_overlap(sess["StartTime"], sess["EndTime"],
                                        assigned_sess["StartTime"], assigned_sess["EndTime"]):
                            conflict_found = True
                            logging.debug(f"Conflict detected for {student_label}: {sess['CourseCode']} overlaps with {assigned_sess['CourseCode']} on {sess['DayOfWeek']}.")
                            break
                    if conflict_found:
                        break
                if conflict_found:
                    continue  # Try next cohort
                
                # Assign this cohort
                assigned_cohorts[course] = cohort
                session_assignments.extend(sessions)
                
                # Proceed to next course
                if backtrack(course_index + 1):
                    return True  # Successful assignment
                
                # Backtrack
                assigned_cohorts.pop(course)
                for sess in sessions:
                    session_assignments.remove(sess)
            
            return False  # No feasible cohort assignment found for this course
        
        # Start backtracking
        feasible = backtrack(0)
        
        if not feasible:
            # Report conflict: No feasible cohort assignments found
            conflict_entry = {
                "Student": student_label,
                "Conflicts": [
                    {
                        "Type": "Cohort Assignment",
                        "Details": "No feasible cohort assignments found without scheduling conflicts."
                    }
                ]
            }
            conflicts.append(conflict_entry)
            logging.info(f"Conflict detected for {student_label}: Cohort Assignment Conflict.")
            continue  # Proceed to next student
        
        # If feasible, collect all assigned sessions for cross-type conflict checks
        for sess in session_assignments:
            student_sessions_map[student_id].append({
                "CourseCode": sess["CourseCode"],
                "SessionType": sess["SessionType"],
                "RoomName": sess["RoomName"],
                "DayOfWeek": sess["DayOfWeek"],
                "StartTime": sess["StartTime"],
                "EndTime": sess["EndTime"],
                "Type": type_
            })
    
    # After assigning cohorts for all (StudentID, Type) pairs, check for cross-type conflicts
    for student_id, sessions in student_sessions_map.items():
        # Fetch student's major and year
        student_info = next((stu for stu in students if stu['StudentID'] == student_id), None)
        if not student_info:
            logging.warning(f"StudentID {student_id} not found in Student table.")
            continue  # Skip if student not found
        
        major_id = student_info['MajorID']
        year_number = student_info['YearNumber']
        major_name = major_map.get(major_id, "Unknown Major")
        
        # Determine all types the student has
        student_types = set(sess["Type"] for sess in sessions)
        
        # Format student label without Type for cross-type conflicts
        student_label = f"StudentID {student_id}, {ordinal(year_number)}-year {major_name}"
        
        # Organize sessions by day
        sessions_by_day = defaultdict(list)
        for sess in sessions:
            sessions_by_day[sess["DayOfWeek"]].append(sess)
        
        # Check each day for maximum sessions
        for day, day_sessions in sessions_by_day.items():
            if len(day_sessions) > 5:
                session_details = [
                    {
                        "CourseCode": sess["CourseCode"],
                        "SessionType": sess["SessionType"],
                        "RoomName": sess["RoomName"],
                        "StartTime": convert_time_to_hhmm(sess["StartTime"]),
                        "EndTime": convert_time_to_hhmm(sess["EndTime"])
                    }
                    for sess in day_sessions
                ]
                conflict_entry = {
                    "Student": student_label,
                    "Conflicts": [
                        {
                            "Type": "Max Sessions Exceeded",
                            "Day": day,
                            "SessionCount": len(day_sessions),
                            "Details": "Cannot attend more than 5 sessions in a day.",
                            "Sessions": session_details
                        }
                    ]
                }
                conflicts.append(conflict_entry)
                logging.warning(f"Max Sessions Exceeded for {student_label} on {day}: {len(day_sessions)} sessions.")
        
        # Check for overlapping sessions across Types
        # Compare each pair of sessions
        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                sessA = sessions[i]
                sessB = sessions[j]
                if sessA["DayOfWeek"] != sessB["DayOfWeek"]:
                    continue
                if times_overlap(sessA["StartTime"], sessA["EndTime"],
                                sessB["StartTime"], sessB["EndTime"]):
                    # Determine if it's a cross-type overlap
                    if sessA["Type"] != sessB["Type"]:
                        conflict_type = "Cross-Type Overlapping Sessions"
                    else:
                        conflict_type = "Overlapping Sessions"
                    
                    # Prepare conflict details
                    conflict = {
                        "Courses": [sessA["CourseCode"], sessB["CourseCode"]],
                        "Details": f"Sessions {sessA['CourseCode']} and {sessB['CourseCode']} overlap in time.",
                        "Sessions": [
                            {
                                "CourseCode": sessA["CourseCode"],
                                "SessionType": sessA["SessionType"],
                                "RoomName": sessA["RoomName"],
                                "StartTime": convert_time_to_hhmm(sessA["StartTime"]),
                                "EndTime": convert_time_to_hhmm(sessA["EndTime"])
                            },
                            {
                                "CourseCode": sessB["CourseCode"],
                                "SessionType": sessB["SessionType"],
                                "RoomName": sessB["RoomName"],
                                "StartTime": convert_time_to_hhmm(sessB["StartTime"]),
                                "EndTime": convert_time_to_hhmm(sessB["EndTime"])
                            }
                        ]
                    }
                    conflict_entry = {
                        "Student": student_label,
                        "Conflicts": [
                            {
                                "Type": conflict_type,
                                "Day": sessA["DayOfWeek"],
                                "Conflicts": [conflict]
                            }
                        ]
                    }
                    conflicts.append(conflict_entry)
                    logging.warning(f"{conflict_type} for {student_label} on {sessA['DayOfWeek']}: {sessA['CourseCode']} and {sessB['CourseCode']}.")

    return conflicts

def save_conflicts_to_json(conflicts, filename='feasibility_conflicts.json'):
    """
    Saves the conflicts list to a JSON file.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(conflicts, f, indent=4)
        logging.info(f"Conflicts have been saved to {filename}")
        print(f"Conflicts have been saved to {filename}")
    except IOError as e:
        logging.error(f"Failed to write conflicts to {filename}: {e}")
        print(f"Failed to write conflicts to {filename}: {e}")

def generate_html_report(conflicts, filename='feasibility_conflicts.html'):
    """
    Generates an HTML report from the conflicts list.
    """
    try:
        with open(filename, 'w') as f:
            f.write("<html><head><title>Feasibility Conflicts Report</title></head><body>")
            f.write("<h1>Feasibility Conflicts Report</h1>")
            if not conflicts:
                f.write("<p>No conflicts detected. All student course selections are feasible.</p>")
            else:
                for conflict in conflicts:
                    f.write("<hr>")
                    f.write(f"<h2>Student: {conflict['Student']}</h2>")
                    for conf_type in conflict["Conflicts"]:
                        f.write(f"<h3>Conflict Type: {conf_type['Type']}</h3>")
                        f.write(f"<p><strong>Day:</strong> {conf_type['Day']}</p>")
                        if conf_type['Type'] in ["Cohort Assignment", "Max Sessions Exceeded"]:
                            f.write(f"<p><strong>Details:</strong> {conf_type['Details']}</p>")
                        if conf_type['Type'] in ["Max Sessions Exceeded", "Overlapping Sessions", "Cross-Type Overlapping Sessions"]:
                            if 'SessionCount' in conf_type:
                                f.write(f"<p><strong>Session Count:</strong> {conf_type['SessionCount']}</p>")
                            if 'Conflicts' in conf_type:
                                for overlap in conf_type['Conflicts']:
                                    f.write(f"<p>{overlap['Details']}</p>")
                                    f.write("<ul>")
                                    for sess in overlap['Sessions']:
                                        f.write(f"<li><strong>{sess['CourseCode']}</strong>: {sess['SessionType']} in {sess['RoomName']} "
                                                f"(Scheduled Time: {sess['StartTime']} - {sess['EndTime']})</li>")
                                    f.write("</ul>")
                        elif conf_type['Type'] == "Cohort Assignment":
                            # List the conflicting courses without specific session details
                            pass
                f.write("</body></html>")
        logging.info(f"HTML report has been saved to {filename}")
        print(f"HTML report has been saved to {filename}")
    except IOError as e:
        logging.error(f"Failed to write HTML report to {filename}: {e}")
        print(f"Failed to write HTML report to {filename}: {e}")

def print_conflicts(conflicts):
    """
    Prints conflicts to the console in a readable format.
    """
    if not conflicts:
        print("No conflicts detected. All student course selections are feasible.")
        return
    
    for conflict in conflicts:
        print("------------------------------------------------------------")
        print(f"Student: {conflict['Student']}")
        for conf in conflict["Conflicts"]:
            print(f"  Conflict Type: {conf['Type']}")
            if 'Day' in conf:
                print(f"    Day: {conf['Day']}")
            if 'SessionCount' in conf:
                print(f"    Session Count: {conf['SessionCount']}")
            if 'Details' in conf:
                print(f"    Details: {conf['Details']}")
            if 'Conflicts' in conf:
                for overlap in conf['Conflicts']:
                    print(f"      - {overlap['Details']}")
                    for sess in overlap['Sessions']:
                        print(f"          * {sess['CourseCode']} ({sess['SessionType']}) in {sess['RoomName']} "
                              f"from {sess['StartTime']} to {sess['EndTime']}")
        print("------------------------------------------------------------\n")

def parse_arguments():
    """
    Parses command-line arguments for output filenames.
    """
    parser = argparse.ArgumentParser(description='Feasibility Checker for Student Course Selections.')
    parser.add_argument('--json', type=str, default='feasibility_conflicts.json',
                        help='Output JSON filename for conflict report.')
    parser.add_argument('--html', type=str, default='feasibility_conflicts.html',
                        help='Output HTML filename for conflict report.')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Configure logging with timestamped filename
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"feasibility_checker_{timestamp}.log"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logging.info("Starting feasibility check.")
    
    try:
        # Run the feasibility check
        outcome = run_feasibility_check()
        
        if not outcome:
            print("No conflicts detected. All student course selections are feasible.")
            logging.info("No conflicts detected.")
        else:
            # Save conflicts to JSON for detailed analysis
            save_conflicts_to_json(outcome, filename=args.json)
            
            # Generate HTML report
            generate_html_report(outcome, filename=args.html)
            
            # Print conflicts to the console for immediate visibility
            print("\nConflict Report:")
            print_conflicts(outcome)
            
            print(f"Please refer to '{args.json}' and '{args.html}' for detailed reports.")
            logging.info("Conflicts detected and reported.")
    except Exception as e:
        logging.error(f"An error occurred during feasibility check: {e}")
        print(f"An error occurred: {e}")