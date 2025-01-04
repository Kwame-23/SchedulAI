# feasibility_checker.py

import mysql.connector
from datetime import timedelta
from collections import defaultdict

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

def run_feasibility_check():
    """
    Main function that checks feasibility for all student groups in the Student table.
    Ensures that no group exceeds five sessions per day.
    Also checks for overlapping sessions within the same day for the group.
    Returns a list of conflict dicts, each containing:
      {
         "StudentGroup": "First-year Computer Science students",
         "MaxSessionsExceeded": {
             "Day": "Monday",
             "SessionCount": 6,
             "Sessions": [
                 {
                     "CourseCode": "CS411",
                     "SessionType": "Lecture",
                     "RoomName": "Room 213",
                     "StartTime": "10:00",
                     "EndTime": "11:00"
                 },
                 ...
             ],
             "Reason": "Cannot attend more than 5 sessions in a day."
         },
         "OverlappingSessions": {
             "Day": "Tuesday",
             "Conflicts": [
                 {
                     "Sessions": [
                         {
                             "CourseCode": "CS422",
                             "SessionType": "Lecture",
                             "RoomName": "Room 214",
                             "StartTime": "10:00",
                             "EndTime": "11:00"
                         },
                         {
                             "CourseCode": "CS411",
                             "SessionType": "Lecture",
                             "RoomName": "Room 213",
                             "StartTime": "10:30",
                             "EndTime": "11:30"
                         }
                     ],
                     "Reason": "Sessions CS422 and CS411 overlap in time."
                 },
                 ...
             ]
         }
      }
    """
    # 1. Fetch final schedule
    final_schedule = fetch_final_schedule()
    
    # 2. Fetch all students
    all_students = fetch_students()
    
    # 3. Group students by (MajorID, YearNumber)
    student_groups = defaultdict(list)  # key: (MajorID, YearNumber), value: list of StudentIDs
    for stu in all_students:
        key = (stu["MajorID"], stu["YearNumber"])
        student_groups[key].append(stu["StudentID"])
    
    # 4. Fetch Major Names
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT MajorID, MajorName FROM Major")
    majors = cursor.fetchall()
    major_map = {m['MajorID']: m['MajorName'] for m in majors}
    cursor.close()
    conn.close()
    
    conflicts = []
    
    for (major_id, year_number), student_ids in student_groups.items():
        major_name = major_map.get(major_id, "Unknown Major")
        student_group_name = f"{ordinal(year_number)}-year {major_name} students"
        
        # Aggregate all courses for this group
        group_courses = set()
        for sid in student_ids:
            courses = fetch_student_courses(sid)
            group_courses.update(courses)
        
        # Aggregate all sessions for these courses
        group_sessions = [
            session for session in final_schedule
            if session["CourseCode"] in group_courses
        ]
        
        # Organize sessions by DayOfWeek
        sessions_by_day = defaultdict(list)
        for sess in group_sessions:
            sessions_by_day[sess["DayOfWeek"]].append(sess)
        
        # Check each day for conflicts
        for day, sessions in sessions_by_day.items():
            day_conflict = {}
            
            # 1. Check for exceeding session limit
            if len(sessions) > 5:
                # Prepare session details
                session_details = [
                    {
                        "CourseCode": sess["CourseCode"],
                        "SessionType": get_session_type(sess["SessionID"]),
                        "RoomName": sess["RoomName"],
                        "StartTime": convert_timedelta_to_hhmm(sess["StartTime"]),
                        "EndTime": convert_timedelta_to_hhmm(sess["EndTime"])
                    }
                    for sess in sessions
                ]
                
                day_conflict["MaxSessionsExceeded"] = {
                    "Day": day,
                    "SessionCount": len(sessions),
                    "Sessions": session_details,
                    "Reason": "Cannot attend more than 5 sessions in a day."
                }
            
            # 2. Check for overlapping sessions
            overlapping_conflicts = []
            for i in range(len(sessions)):
                for j in range(i+1, len(sessions)):
                    sessA = sessions[i]
                    sessB = sessions[j]
                    if times_overlap(sessA["StartTime"], sessA["EndTime"],
                                    sessB["StartTime"], sessB["EndTime"]):
                        conflict = {
                            "Sessions": [
                                {
                                    "CourseCode": sessA["CourseCode"],
                                    "SessionType": get_session_type(sessA["SessionID"]),
                                    "RoomName": sessA["RoomName"],
                                    "StartTime": convert_timedelta_to_hhmm(sessA["StartTime"]),
                                    "EndTime": convert_timedelta_to_hhmm(sessA["EndTime"])
                                },
                                {
                                    "CourseCode": sessB["CourseCode"],
                                    "SessionType": get_session_type(sessB["SessionID"]),
                                    "RoomName": sessB["RoomName"],
                                    "StartTime": convert_timedelta_to_hhmm(sessB["StartTime"]),
                                    "EndTime": convert_timedelta_to_hhmm(sessB["EndTime"])
                                }
                            ],
                            "Reason": f"Sessions {sessA['CourseCode']} and {sessB['CourseCode']} overlap in time."
                        }
                        # To avoid duplicate conflict entries
                        if conflict not in overlapping_conflicts:
                            overlapping_conflicts.append(conflict)
            
            if overlapping_conflicts:
                day_conflict["OverlappingSessions"] = {
                    "Day": day,
                    "Conflicts": overlapping_conflicts
                }
            
            # If any conflict exists for the day, add to the conflicts list
            if day_conflict:
                conflict_entry = {
                    "StudentGroup": student_group_name
                }
                if "MaxSessionsExceeded" in day_conflict:
                    conflict_entry["MaxSessionsExceeded"] = day_conflict["MaxSessionsExceeded"]
                if "OverlappingSessions" in day_conflict:
                    conflict_entry["OverlappingSessions"] = day_conflict["OverlappingSessions"]
                conflicts.append(conflict_entry)
    
    return conflicts

def ordinal(n):
    """
    Converts an integer into its ordinal representation:
    1 -> "First", 2 -> "Second", etc.
    """
    ordinals = {1: "First", 2: "Second", 3: "Third",
                4: "Fourth", 5: "Fifth", 6: "Sixth",
                7: "Seventh", 8: "Eighth", 9: "Ninth",
                10: "Tenth"}
    return ordinals.get(n, f"{n}th")

def get_session_type(session_id):
    """
    Fetches the SessionType for a given SessionID from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SessionType
        FROM SessionAssignments
        WHERE SessionID = %s
    """, (session_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else "Unknown Type"

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

if __name__ == "__main__":
    # If you run this script directly, just print conflicts
    outcome = run_feasibility_check()
    for conflict in outcome:
        print("Conflict Detected:")
        print(f"- Student Group: {conflict['StudentGroup']}")
        if "MaxSessionsExceeded" in conflict:
            me = conflict["MaxSessionsExceeded"]
            print(f"- Maximum Sessions Exceeded: {me['Reason']}")
            print("- Conflicting Sessions:")
            for sess in me["Sessions"]:
                print(f"  - {sess['CourseCode']}: {sess['SessionType']} in {sess['RoomName']} (Scheduled Time: {sess['StartTime']} - {sess['EndTime']})")
        if "OverlappingSessions" in conflict:
            os = conflict["OverlappingSessions"]
            print("- Overlapping Sessions:")
            for oc in os["Conflicts"]:
                print(f"  - {oc['Reason']}")
                for sess in oc["Sessions"]:
                    print(f"    * {sess['CourseCode']}: {sess['SessionType']} in {sess['RoomName']} (Scheduled Time: {sess['StartTime']} - {sess['EndTime']})")
        print()