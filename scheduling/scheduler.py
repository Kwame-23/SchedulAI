# ------------------------------------------------------
# Please ensure you have installed:
#     pip install ortools
#     pip install mysql-connector-python
#
# Place this script in your environment or project.
# ------------------------------------------------------

import pandas as pd
from ortools.sat.python import cp_model
import mysql.connector
import re
from datetime import datetime
import os
import logging

# ----------------------------------------------------
# 1. MySQL Database Connection
# ----------------------------------------------------
def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
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
        print(f"Error: {err}")
        return None

# ----------------------------------------------------
# 2. Helper: Normalize "0 days HH:MM:SS" if present
# ----------------------------------------------------
def normalize_duration_str(duration_str: str) -> str:
    """
    Converts strings like "0 days 01:30:00" into "01:30:00".
    If there's a non-zero day part (e.g. "1 days 02:00:00"),
    this simply drops the '1 days' portion and keeps "02:00:00".
    """
    duration_str = duration_str.strip()

    # If the string contains "days", remove that leading portion.
    # Example: "0 days 01:30:00" -> "01:30:00"
    if 'days' in duration_str.lower():
        parts = duration_str.split()
        # parts might be ["0", "days", "01:30:00"]
        # just rejoin everything after "days"
        if len(parts) >= 3 and parts[1].lower() == 'days':
            duration_str = ' '.join(parts[2:])
            # Now it's "01:30:00"

    return duration_str

# ----------------------------------------------------
# 3. Fetch Data from DB and CSV
# ----------------------------------------------------
def fetch_data(session_preferences_csv_path):
    """
    Fetches data from the SessionAssignments table, 
    fetches active rooms (Room.ActiveFlag=1),
    and reads session preferences from the CSV file.
    """
    # 3A. Connect to DB
    conn = get_db_connection()
    if conn is None:
        raise Exception("Failed to connect to the database.")
    
    cursor = conn.cursor(dictionary=True)  # Use dict cursor

    # 3B. Fetch sessions from SessionAssignments
    cursor.execute("""
        SELECT SessionID, CourseCode, CohortName, LecturerName,
               SessionType, Duration, NumberOfEnrollments
        FROM SessionAssignments
    """)
    sessions = cursor.fetchall()
    sessions_df = pd.DataFrame(sessions)
    
    # Convert Duration column to string
    sessions_df['Duration'] = sessions_df['Duration'].astype(str)

    # 3C. Fetch active rooms
    cursor.execute("""
        SELECT RoomID, Location, MaxRoomCapacity
        FROM Room
        WHERE ActiveFlag = 1
    """)
    rooms = cursor.fetchall()
    rooms_df = pd.DataFrame(rooms)

    # Close DB
    cursor.close()
    conn.close()

    # 3D. Read session preferences from the database
    conn = get_db_connection()
    if conn is None:
        logging.error("Database connection not established for session preferences.")
        raise Exception("Database connection error.")

    # Query only the necessary columns from SessionLocationPreferences
    query = "SELECT CourseCode, CourseName, Location, SessionType FROM SessionLocationPreferences"
    session_preferences_data = pd.read_sql(query, conn)
    conn.close()

    logging.info("Session preferences data fetched successfully from the database.")
    return sessions_df, rooms_df, session_preferences_data

# ----------------------------------------------------
# 4. Convert Duration to # of 15-min Blocks
# ----------------------------------------------------
def duration_to_blocks(duration_str, time_blocks=15):
    """
    Converts a duration from "HH:MM:SS" (or "0 days HH:MM:SS")
    into the number of 15-minute blocks. Raises ValueError if invalid.
    """
    # Normalize e.g. "0 days 01:30:00" -> "01:30:00"
    duration_str = normalize_duration_str(duration_str)

    parts = duration_str.strip().split(':')
    if len(parts) < 2:
        raise ValueError(f"Invalid duration format: {duration_str}")

    hours, minutes = map(int, parts[:2])  # parse HH and MM
    total_minutes  = hours * 60 + minutes
    return total_minutes // time_blocks

# ----------------------------------------------------
# 5. Assign Single Session
# ----------------------------------------------------
def assign_session(
    session, 
    room, 
    start_block,
    room_occupancy,
    lecturer_schedule,
    scheduled_session_ids,
    course_cohort_schedule,
    scheduled_lectures,
    assigned_sessions,
    day,
    time_blocks,
    start_time
):
    """
    Assigns a single session to `room` starting at `start_block`,
    updating all data structures. Returns True on success.
    """
    # 5A. Figure out end_block
    end_block = start_block + duration_to_blocks(session['Duration'], time_blocks)

    # 5B. Build session details
    start_hr    = (start_time + start_block * time_blocks) // 60
    start_min   = (start_time + start_block * time_blocks) % 60
    end_hr      = (start_time + end_block   * time_blocks) // 60
    end_min     = (start_time + end_block   * time_blocks) % 60

    session_details = {
        "Session ID":   session['SessionID'],
        "Course Code":  session['CourseCode'],
        "Cohort":       session['CohortName'],
        "Lecturer":     session['LecturerName'],
        "Room":         room,
        "Start Time":   f"{start_hr:02d}:{start_min:02d}",
        "End Time":     f"{end_hr:02d}:{end_min:02d}",
        "Day":          day
    }

    # 5C. Store assignment
    assigned_sessions.append(session_details)

    # 5D. Mark room occupancy
    for block in range(start_block, end_block):
        room_occupancy[day][room][block] = session['SessionID']

    # 5E. Mark lecturer occupancy
    lecturer_name = session['LecturerName']
    for block in range(start_block, end_block):
        lecturer_schedule[day].setdefault(lecturer_name, {})[block] = session['SessionID']

    # 5F. Mark session as assigned
    scheduled_session_ids.add(session['SessionID'])

    # 5G. Mark course-cohort scheduled
    course_code  = session['CourseCode']
    cohort_name  = session['CohortName']
    course_cohort_schedule[day].add( (course_code, cohort_name) )

    # 5H. If this is a lecture, store consistent scheduling info
    if session['SessionType'].lower() == 'lecture':
        scheduled_lectures[(course_code, cohort_name, session['SessionType'])] = {
            "Room":          room,
            "Start Block":   start_block,
            "Duration Blocks": (end_block - start_block),
            "Start Time":    session_details["Start Time"],
            "End Time":      session_details["End Time"]
        }

    return True

# ----------------------------------------------------
# Store Unassigned Sessions in UnassignedSessions Table
# ----------------------------------------------------
def store_unassigned_sessions(unassigned_list):
    """
    Inserts unassigned sessions into the UnassignedSessions table.
    unassigned_list is a list of rows from the leftover sessions (tuples).
    
    Each row has the structure: (SessionID, CourseCode, CohortName, LecturerName, SessionType, Duration, NumberOfEnrollments)
    """
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to DB to store unassigned sessions.")
        return
    
    cursor = conn.cursor()
    
    insert_sql = """
        INSERT INTO UnassignedSessions
        (SessionID, CourseCode, LecturerName, CohortName, SessionType, Duration, NumberOfEnrollments)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    for row in unassigned_list:
        # row = (SessionID, CourseCode, CohortName, LecturerName, SessionType, Duration, NumberOfEnrollments)
        session_id = row[0]
        course_code = row[1]
        cohort_name = row[2]
        lecturer_name = row[3]
        session_type = row[4]
        duration_raw = row[5]
        enrollments = row[6]
        
        # Normalize Duration
        duration = normalize_duration_str(str(duration_raw))
        
        # Validate Duration format (optional but recommended)
        if not re.match(r'^\d{2}:\d{2}:\d{2}$', duration):
            print(f"Invalid Duration format for SessionID {session_id}: {duration}")
            continue  # Skip inserting this row or handle as needed
    
        cursor.execute(insert_sql, (
            session_id,
            course_code,
            lecturer_name,
            cohort_name,
            session_type,
            duration,
            enrollments
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Unassigned sessions have been stored in UnassignedSessions table.")

# ----------------------------------------------------
# 6A. Function to Write the Final Schedule to DB
# ----------------------------------------------------
def write_schedule_to_db(assigned_sessions):
    """
    Inserts the final assigned schedule into both the SessionSchedule and UpdatedSessionSchedule tables.
    Each entry in assigned_sessions is a dict with:
    {
        "Session ID": 206,
        "Course Code": "CS313",
        "Cohort": "Section B",
        "Lecturer": "Umut Tosun",
        "Room": "Jackson Hall 115",
        "Day": "Friday",
        "Start Time": "08:00",
        "End Time": "09:30"
    }
    """
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to DB to store schedule.")
        return

    cursor = conn.cursor()

    # Define SQL queries for inserting into both tables.
    insert_sql = """
    INSERT INTO SessionSchedule (SessionID, DayOfWeek, StartTime, EndTime, RoomName)
    VALUES (%s, %s, %s, %s, %s)
    """
    insert_staging_sql = """
    INSERT INTO UpdatedSessionSchedule (SessionID, DayOfWeek, StartTime, EndTime, RoomName)
    VALUES (%s, %s, %s, %s, %s)
    """

    # Loop through each assigned session and insert into both tables.
    for s in assigned_sessions:
        session_id  = s["Session ID"]
        day_of_week = s["Day"]
        start_time  = s["Start Time"]
        end_time    = s["End Time"]
        room_name   = s["Room"]

        # Insert into SessionSchedule
        cursor.execute(insert_sql, (session_id, day_of_week, start_time, end_time, room_name))
        # Insert into UpdatedSessionSchedule
        cursor.execute(insert_staging_sql, (session_id, day_of_week, start_time, end_time, room_name))

    conn.commit()
    cursor.close()
    conn.close()
    print("Schedule has been written to both SessionSchedule and UpdatedSessionSchedule tables.")

# ----------------------------------------------------
# 6B. Main Scheduling Function
# ----------------------------------------------------
def schedule_sessions(session_preferences_csv_path):
    """
    Main scheduling routine:
      1) Fetch sessions, rooms, preferences
      2) Sort them
      3) Prepare data structures
      4) Loop day-by-day, session-by-session to assign
      5) Print results
      6) Write final schedule to SessionSchedule table
    """
    # 6B-1. Fetch data
    sessions_df, rooms_df, session_preferences_df = fetch_data(session_preferences_csv_path)
    print("Data fetched successfully from the database and CSV.")

    print("Rooms DataFrame columns:", rooms_df.columns)
    print("Number of rooms fetched:", len(rooms_df))
    # 6B-2. Sort rooms & sessions
    rooms_df.rename(columns={'roomid': 'RoomID', 'location': 'Location', 'maxroomcapacity': 'MaxRoomCapacity'}, inplace=True)
    rooms_df = rooms_df.sort_values(by='MaxRoomCapacity', ascending=False)
    sessions_df = sessions_df.sort_values(by='NumberOfEnrollments', ascending=False)

    # 6B-3. Time definitions
    start_time        = 8 * 60    # 8 AM in minutes
    end_time          = 17 * 60   # 5 PM in minutes
    morning_end_time  = 12 * 60   # 12 PM
    time_blocks       = 15
    time_slots_per_day= (end_time - start_time) // time_blocks
    days_of_week      = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # 6B-4. Build occupancy/schedule data structures
    room_occupancy = {
        day: { loc: [None]*time_slots_per_day for loc in rooms_df['Location'] }
        for day in days_of_week
    }
    scheduled_session_ids = set()
    unassigned_sessions   = []  # We'll store the full row from sessions_df here
    assigned_sessions     = []

    # 6B-5. Build a dictionary of "preferred rooms" for each course code
    preferred_rooms = session_preferences_df.groupby('CourseCode')['Location'].apply(list).to_dict()

    # 6B-6. Additional tracking
    lecturer_schedule      = {day:{} for day in days_of_week}
    course_cohort_schedule = {day:set() for day in days_of_week}
    scheduled_lectures     = {}

    # 6B-7. Loop over days
    for day in days_of_week:
        # 6B-7a. Loop over sessions
        for _, sess in sessions_df.iterrows():
            session_id   = sess['SessionID']
            course_code  = sess['CourseCode']
            cohort_name  = sess['CohortName']
            session_type = sess['SessionType']
            lecturer_name= sess['LecturerName']
            duration_str = sess['Duration']
            enrollments  = sess['NumberOfEnrollments']

            # Already assigned or same course-cohort on day
            if (session_id in scheduled_session_ids or
                (course_code, cohort_name) in course_cohort_schedule[day]):
                continue

            # Check if lecture schedule already exists
            lecture_key = (course_code, cohort_name, session_type)
            if session_type.lower()=='lecture' and lecture_key in scheduled_lectures:
                existing_info = scheduled_lectures[lecture_key]
                used_room     = existing_info['Room']
                used_startblk = existing_info['Start Block']
                used_durblks  = existing_info['Duration Blocks']
                used_endblk   = used_startblk + used_durblks

                # Check if that same slot is free
                room_free = all(
                    room_occupancy[day][used_room][blk] is None
                    for blk in range(used_startblk, used_endblk)
                )
                lect_free = all(
                    lecturer_schedule[day].get(lecturer_name,{}).get(blk) is None
                    for blk in range(used_startblk, used_endblk)
                )
                if room_free and lect_free:
                    ok = assign_session(
                        sess, used_room, used_startblk,
                        room_occupancy, lecturer_schedule,
                        scheduled_session_ids, course_cohort_schedule,
                        scheduled_lectures, assigned_sessions,
                        day, time_blocks, start_time
                    )
                    if ok:
                        print(f"Assigned Session ID {session_id} to consistent room {used_room} "
                              f"at {existing_info['Start Time']} - {existing_info['End Time']} on {day}.")
                    continue
                else:
                    print(f"Unable to assign {course_code} - conflict with consistent scheduling.")
                    unassigned_sessions.append(sess)  # full row
                    continue

            # 6B-7b. Attempt to parse duration
            try:
                dur_blocks = duration_to_blocks(duration_str, time_blocks)
            except ValueError as vex:
                print(f"Session ID {session_id}: {vex}")
                unassigned_sessions.append(sess)
                continue

            session_assigned = False
            print(f"Attempting to schedule Session ID {session_id} - {course_code}...")

            def do_assign(rm, blk):
                nonlocal session_assigned
                return assign_session(
                    sess, rm, blk,
                    room_occupancy, lecturer_schedule,
                    scheduled_session_ids, course_cohort_schedule,
                    scheduled_lectures, assigned_sessions,
                    day, time_blocks, start_time
                )

            def check_break_ok(rm, blk):
                if blk > 0 and room_occupancy[day][rm][blk-1] is not None:
                    return False
                return True

            # 6B-7c. Handle Friday special constraints
            if day == 'Friday':
                prayer_start    = 11*60 + 50  # 11:50 AM
                prayer_end      = 12*60 + 15  # 12:15 PM
                latest_end_time = 15*60 + 25  # 3:25 PM
                p_start_block   = (prayer_start - start_time)//time_blocks
                p_end_block     = (prayer_end   - start_time)//time_blocks
                latest_end_block= (latest_end_time - start_time)//time_blocks

                if dur_blocks <= p_start_block:
                    # Try scheduling before prayer
                    for pref_room in preferred_rooms.get(course_code, []):
                        for blk in range(p_start_block - dur_blocks + 1):
                            blocks_free = all(
                                room_occupancy[day][pref_room][b] is None
                                for b in range(blk, blk+dur_blocks)
                            )
                            if blocks_free and check_break_ok(pref_room, blk):
                                session_assigned = do_assign(pref_room, blk)
                                break
                        if session_assigned:
                            break

                    if not session_assigned:
                        # try after prayer
                        for pref_room in preferred_rooms.get(course_code, []):
                            for blk in range(p_end_block, latest_end_block - dur_blocks +1):
                                blocks_free = all(
                                    room_occupancy[day][pref_room][b] is None
                                    for b in range(blk, blk+dur_blocks)
                                )
                                if blocks_free and check_break_ok(pref_room, blk):
                                    session_assigned = do_assign(pref_room, blk)
                                    break
                            if session_assigned:
                                break

                if not session_assigned:
                    print(f"Unable to schedule {course_code} - Friday conflict.")
                    unassigned_sessions.append(sess)
                    continue

            # 6B-7d. If MATH => morning preference
            elif 'MATH' in course_code.upper():
                morning_blocks = (morning_end_time - start_time)//time_blocks
                for pref_room in preferred_rooms.get(course_code, []):
                    if pref_room not in room_occupancy[day]:
                        continue
                    for blk in range(morning_blocks):
                        if blk + dur_blocks <= morning_blocks:
                            capacity_ok  = (
                                rooms_df[rooms_df['Location']==pref_room]['MaxRoomCapacity'].values[0]
                                >= enrollments
                            )
                            blocks_free  = all(
                                room_occupancy[day][pref_room][b] is None
                                for b in range(blk, blk+dur_blocks)
                            )
                            lecturer_free= all(
                                lecturer_schedule[day].get(lecturer_name,{}).get(b) is None
                                for b in range(blk, blk+dur_blocks)
                            )
                            if capacity_ok and blocks_free and lecturer_free and check_break_ok(pref_room, blk):
                                session_assigned = do_assign(pref_room, blk)
                                break
                    if session_assigned:
                        print(f"Assigned Session ID {session_id} to {pref_room} in the morning.")
                        break

                if not session_assigned:
                    # try other time
                    for pref_room in preferred_rooms.get(course_code, []):
                        for blk in range(morning_blocks, time_slots_per_day):
                            if blk + dur_blocks <= time_slots_per_day:
                                capacity_ok  = (
                                    rooms_df[rooms_df['Location']==pref_room]['MaxRoomCapacity'].values[0]
                                    >= enrollments
                                )
                                blocks_free  = all(
                                    room_occupancy[day][pref_room][b] is None
                                    for b in range(blk, blk+dur_blocks)
                                )
                                lecturer_free= all(
                                    lecturer_schedule[day].get(lecturer_name,{}).get(b) is None
                                    for b in range(blk, blk+dur_blocks)
                                )
                                if capacity_ok and blocks_free and lecturer_free and check_break_ok(pref_room, blk):
                                    session_assigned = do_assign(pref_room, blk)
                                    print(f"Assigned Math course {course_code} outside morning hours.")
                                    break
                        if session_assigned:
                            break

            # 6B-7e. For non-Math or leftover, attempt preferred rooms
            if not session_assigned:
                for pref_room in preferred_rooms.get(course_code, []):
                    blk = 0
                    while blk + dur_blocks + 1 <= time_slots_per_day:
                        capacity_ok  = (
                            rooms_df[rooms_df['Location']==pref_room]['MaxRoomCapacity'].values[0]
                            >= enrollments
                        )
                        blocks_free  = all(
                            room_occupancy[day][pref_room][b] is None
                            for b in range(blk, blk+dur_blocks)
                        )
                        lecturer_free= all(
                            lecturer_schedule[day].get(lecturer_name,{}).get(b) is None
                            for b in range(blk, blk+dur_blocks)
                        )
                        if capacity_ok and blocks_free and lecturer_free and check_break_ok(pref_room, blk):
                            session_assigned = do_assign(pref_room, blk)
                            break
                        blk += 1
                    if session_assigned:
                        print(f"Assigned Session ID {session_id} to preferred room {pref_room}")
                        break

            # 6B-7f. Fallback to any room
            if not session_assigned:
                for fallback_rm in rooms_df['Location']:
                    blk = 0
                    while blk + dur_blocks + 1 <= time_slots_per_day:
                        capacity_ok  = (
                            rooms_df[rooms_df['Location']==fallback_rm]['MaxRoomCapacity'].values[0]
                            >= enrollments
                        )
                        blocks_free  = all(
                            room_occupancy[day][fallback_rm][b] is None
                            for b in range(blk, blk+dur_blocks)
                        )
                        lecturer_free= all(
                            lecturer_schedule[day].get(lecturer_name,{}).get(b) is None
                            for b in range(blk, blk+dur_blocks)
                        )
                        if capacity_ok and blocks_free and lecturer_free and check_break_ok(fallback_rm, blk):
                            session_assigned = do_assign(fallback_rm, blk)
                            print(f"Assigned Session ID {session_id} to fallback room {fallback_rm}")
                            break
                        blk += 1
                    if session_assigned:
                        break

            # 6B-7g. If STILL not assigned => unassigned
            if not session_assigned:
                unassigned_sessions.append(sess)
                print(f"Unable to assign Session ID {session_id} - added to unassigned sessions.")

    # 6B-8. Deduplicate & sort assigned sessions
    unique_map = {}
    for s in assigned_sessions:
        key = (s['Session ID'], s['Room'], s['Day'])
        unique_map[key] = s
    assigned_sessions = list(unique_map.values())
    assigned_sessions_sorted = sorted(assigned_sessions, key=lambda x: x['Session ID'])

    # 6B-9. Print final schedule
    print("\nComplete Timetable of All Scheduled Sessions in Ascending Order by Session ID:")
    for s in assigned_sessions_sorted:
        print(f"Session ID: {s['Session ID']}, Course Code: {s['Course Code']}, "
              f"Cohort: {s['Cohort']}, Lecturer: {s['Lecturer']}, Room: {s['Room']}, "
              f"Day: {s['Day']}, Start Time: {s['Start Time']}, End Time: {s['End Time']}")

    # 6B-9b: Identify leftover (unassigned) sessions
    leftover = [
        row for row in sessions_df.itertuples(index=False, name=None)
        if row[0] not in scheduled_session_ids
    ]
    if not leftover:
        print("All sessions have been scheduled.")
    else:
        print("The following sessions could not be scheduled:")
        for row in leftover:
            print(f"Session ID: {row[0]}, Course Code: {row[1]}, "
                  f"Cohort: {row[2]}, Lecturer: {row[3]}, "
                  f"Duration: {row[4]}, Number of Enrollments: {row[5]}")
    
        # 6B-9c: Insert leftover into UnassignedSessions table
        store_unassigned_sessions(leftover)

    # 6B-10. Print room occupancies
    print("\nRoom Occupancies:")
    for day, room_dict in room_occupancy.items():
        print(f"\n--- {day} ---")
        for rm, occupancy in room_dict.items():
            print(f"\nRoom: {rm}")
            for blk, sid in enumerate(occupancy):
                blk_start_hr = (start_time + blk*time_blocks)//60
                blk_start_mn = (start_time + blk*time_blocks)%60
                blk_start_str= f"{blk_start_hr:02d}:{blk_start_mn:02d}"

                if sid is not None and sid != 'BREAK':
                    print(f"  Time Block {blk} ({blk_start_str}): Session ID {sid}")
                elif sid=='BREAK':
                    print(f"  Time Block {blk} ({blk_start_str}): BREAK")
                else:
                    print(f"  Time Block {blk} ({blk_start_str}): Free")

    # Sort final schedule by day & start time
    def parse_time(ts: str):
        return datetime.strptime(ts, "%H:%M")

    sorted_schedule = sorted(
        assigned_sessions,
        key=lambda x: (days_of_week.index(x['Day']), parse_time(x['Start Time']))
    )

    print("\nFinal Schedule by Day and Start Time:")
    current_day = None
    for s in sorted_schedule:
        if s['Day'] != current_day:
            current_day = s['Day']
            print(f"\n--- {current_day} ---")
        print(f"Session ID: {s['Session ID']}, Course Code: {s['Course Code']}, "
              f"Cohort: {s['Cohort']}, Lecturer: {s['Lecturer']}, Room: {s['Room']}, "
              f"Start Time: {s['Start Time']}, End Time: {s['End Time']}")

    # 6B-11. Write final schedule to DB
    write_schedule_to_db(assigned_sessions_sorted)