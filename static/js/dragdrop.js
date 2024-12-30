// dragdrop.js

document.addEventListener("DOMContentLoaded", () => {
    // 1. Parse session data from the hidden script tag
    const sessionDataScript = document.getElementById("session-data");
    const sessions = JSON.parse(sessionDataScript.textContent || '[]');
  
    // 2. Populate the timetable with session blocks
    sessions.forEach(sess => {
      createSessionBlock(sess);
    });
  
    // 3. Initialize drag-and-drop event listeners
    initDragAndDrop();
  
    // 4. Save button
    const saveButton = document.getElementById("save-button");
    saveButton.addEventListener("click", handleSave);
  });
  
  /**
   * createSessionBlock: Creates a .session-block div and places it in the correct .timeslot
   */
  function createSessionBlock(sess) {
    // Example session object:
    // { "SessionID": 206, "CourseCode": "CS313", "SessionType": "Lecture", 
    //   "DayOfWeek":"Monday", "StartTime":"08:00", "EndTime":"09:30", "Lecturer":"Umut Tosun", etc. }
  
    // Find the correct day column 
    const dayColumn = document.querySelector(`.day-column[data-day="${sess.DayOfWeek}"]`);
    if (!dayColumn) return; // if no day match
  
    // Find the timeslot with data-start = sess.StartTime
    const slot = dayColumn.querySelector(`.timeslot[data-start="${sess.StartTime}"]`);
    if (!slot) return; // if no timeslot match
  
    // Create the block
    const block = document.createElement('div');
    block.classList.add('session-block');
    block.setAttribute('draggable', 'true');
    block.dataset.sessionId = sess.SessionID;
    block.dataset.courseCode = sess.CourseCode;
    block.dataset.sessionType = sess.SessionType || "Lecture";
    block.dataset.day = sess.DayOfWeek;
    block.dataset.start = sess.StartTime;
    block.dataset.end = sess.EndTime;
    block.dataset.lecturer = sess.Lecturer || "";
    block.innerHTML = `
      <strong>${sess.CourseCode}</strong> (${sess.SessionType})<br>
      ${sess.Lecturer || 'Lecturer N/A'}<br>
      ${sess.StartTime} - ${sess.EndTime}
    `;
  
    // Position it (if you want absolute positioning, you might set style.top, etc.)
    slot.appendChild(block);
  }
  
  /**
   * initDragAndDrop: set up dragstart, dragover, drop, etc.
   */
  function initDragAndDrop() {
    // 1. Draggable blocks
    const sessionBlocks = document.querySelectorAll('.session-block');
    sessionBlocks.forEach(block => {
      block.addEventListener('dragstart', handleDragStart);
    });
  
    // 2. Droppable timeslots
    const timeslots = document.querySelectorAll('.timeslot');
    timeslots.forEach(slot => {
      slot.addEventListener('dragover', (e) => e.preventDefault());
      slot.addEventListener('drop', handleDrop);
    });
  }
  
  function handleDragStart(e) {
    // store the session ID and original day/time
    const block = e.target;
    e.dataTransfer.setData('text/plain', block.dataset.sessionId);
    // We could store old day/time if we want to revert on conflict
    block.dataset.oldDay = block.dataset.day;
    block.dataset.oldStart = block.dataset.start;
  }
  
  function handleDrop(e) {
    e.preventDefault();
    const sessionId = e.dataTransfer.getData('text/plain');
    const block = document.querySelector(`.session-block[data-session-id="${sessionId}"]`);
    if (!block) return;
  
    // Move to new slot
    e.currentTarget.appendChild(block);
  
    // Update block's data-day/data-start
    const newDay = e.currentTarget.closest('.day-column').dataset.day;
    const newStart = e.currentTarget.dataset.start;
    block.dataset.day = newDay;
    block.dataset.start = newStart;
  
    // Conflict check
    checkConflict(block, newDay, newStart);
  }
  
  /**
   * checkConflict: optionally calls a back-end route /check_conflict
   */
  function checkConflict(block, newDay, newStart) {
    // Example call to /check_conflict
    const payload = {
      "SessionID": block.dataset.sessionId,
      "NewDay": newDay,
      "NewStartTime": newStart
    };
  
    fetch("/check_conflict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(resp => resp.json())
    .then(data => {
      if (data.conflict) {
        alert(`Conflict: ${data.reason}`);
        // revert block to old day/time
        revertBlock(block);
      }
    })
    .catch(err => console.error("Conflict check error:", err));
  }
  
  function revertBlock(block) {
    const oldDay = block.dataset.oldDay;
    const oldStart = block.dataset.oldStart;
    // Move it back
    const dayColumn = document.querySelector(`.day-column[data-day="${oldDay}"]`);
    const oldSlot = dayColumn.querySelector(`.timeslot[data-start="${oldStart}"]`);
    oldSlot.appendChild(block);
  
    block.dataset.day = oldDay;
    block.dataset.start = oldStart;
  }
  
  /**
   * handleSave: collect final positions and send to /save_timetable
   */
  function handleSave() {
    // Gather all session-blocks' day/time
    const blocks = document.querySelectorAll('.session-block');
    const timetableData = [];
    blocks.forEach(b => {
      timetableData.push({
        SessionID: b.dataset.sessionId,
        DayOfWeek: b.dataset.day,
        StartTime: b.dataset.start,
        // Optionally EndTime? We might keep same duration as old or do a calc
        EndTime: b.dataset.end // or compute end from duration
      });
    });
  
    fetch("/save_timetable", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(timetableData)
    })
    .then(resp => resp.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
      }
    })
    .catch(err => console.error("Save error:", err));
  }