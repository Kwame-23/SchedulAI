import mysql.connector
from datetime import datetime, timedelta

def get_db_connection():
    """
    Returns a MySQL connection object to the 'schedulai' database.
    """
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Naakey057@',
        database='schedulai'
    )
    return conn

def fetch_final_schedule():
    """
    Joins SessionAssignments + SessionSchedule to get day/time for each session.
    Returns a list of dicts, each with:
      {
        'SessionID': 123,
        'CourseCode': 'CS111',
        'DayOfWeek': 'Monday',
        'StartTime': timedelta(...)   <-- from MySQL TIME
        'EndTime':   timedelta(...)   <-- from MySQL TIME
        'RoomName': 'Jackson Hall 115'
      }
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT sa.SessionID,
               sa.CourseCode,
               ss.DayOfWeek,
               ss.StartTime,   -- MySQL TIME => Python timedelta
               ss.EndTime,     -- MySQL TIME => Python timedelta
               ss.RoomName
        FROM SessionAssignments AS sa
        JOIN SessionSchedule AS ss ON sa.SessionID = ss.SessionID
        ORDER BY sa.SessionID
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fetch_students():
    """
    Fetch every student from the 'Student' table.
    Each student has:
      StudentID, MajorID, YearNumber
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT StudentID, MajorID, YearNumber FROM Student")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students

def fetch_student_courses(student_id):
    """
    Returns a list of CourseCodes from the bridging table 'StudentCourseSelection'
    for the given StudentID.
    Example: ['CS111', 'MATH101', 'BUSA161_A', ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CourseCode
        FROM StudentCourseSelection
        WHERE StudentID = %s
    """, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # rows is a list of tuples, like [('CS111',), ('MATH101',)]
    return [r[0] for r in rows]

def times_overlap(startA, endA, startB, endB):
    """
    Given start/end times in Python timedelta form (from MySQL TIME fields),
    returns True if intervals overlap, else False.
    """

    def td_to_minutes(td: timedelta) -> int:
        return int(td.total_seconds() // 60)

    sa = td_to_minutes(startA)
    ea = td_to_minutes(endA)
    sb = td_to_minutes(startB)
    eb = td_to_minutes(endB)

    # Two intervals [sa, ea) and [sb, eb) overlap if they are not strictly disjoint
    # i.e. overlap = not (ea <= sb or eb <= sa)
    return not (ea <= sb or eb <= sa)

def check_feasibility_for_student(student, final_schedule):
    """
    1) Determine which courses the student is actually taking (via bridging table).
    2) Gather all sessions for those courses in the final schedule.
    3) Check for day/time overlaps.
    Returns True if feasible, or False if conflict found.
    """
    student_id = student["StudentID"]

    # 1. Fetch the actual courses from bridging table
    enrolled_codes = fetch_student_courses(student_id)

    # 2. Filter final schedule for these course codes
    relevant_sessions = [
        row for row in final_schedule
        if row["CourseCode"] in enrolled_codes
    ]

    # 3. Check pairwise for overlaps if same DayOfWeek
    for i in range(len(relevant_sessions)):
        for j in range(i+1, len(relevant_sessions)):
            if relevant_sessions[i]["DayOfWeek"] == relevant_sessions[j]["DayOfWeek"]:
                if times_overlap(
                    relevant_sessions[i]["StartTime"], relevant_sessions[i]["EndTime"],
                    relevant_sessions[j]["StartTime"], relevant_sessions[j]["EndTime"]
                ):
                    return False  # conflict => not feasible
    return True

def run_feasibility_check():
    """
    Main function that checks feasibility for all students in the Student table.
    Returns a list of dict, each containing:
      {
         "StudentID": X,
         "MajorID": Y,
         "YearNumber": Z,
         "IsFeasible": True/False
      }
    """
    # 1. final schedule
    final_schedule = fetch_final_schedule()
    # 2. all students
    all_students = fetch_students()

    results = []
    for stu in all_students:
        feasible = check_feasibility_for_student(stu, final_schedule)
        results.append({
            "StudentID": stu["StudentID"],
            "MajorID": stu["MajorID"],
            "YearNumber": stu["YearNumber"],
            "IsFeasible": feasible
        })
    return results

if __name__ == "__main__":
    # If you run this script directly, just print results
    outcome = run_feasibility_check()
    for row in outcome:
        s_id = row["StudentID"]
        maj = row["MajorID"]
        yr  = row["YearNumber"]
        ok  = row["IsFeasible"]
        print(f"StudentID={s_id} (MajorID={maj}, Year={yr}) => {'OK' if ok else 'CONFLICT'}")