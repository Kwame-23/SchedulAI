// static/js/main.js

// Function to show session details in a modal
function showSessionDetails(courseCode, lecturer, sessionType, room, time) {
    document.getElementById('modal-course-code').innerText = courseCode;
    document.getElementById('modal-lecturer').innerText = lecturer;
    document.getElementById('modal-session-type').innerText = sessionType;
    document.getElementById('modal-room').innerText = room;
    document.getElementById('modal-time').innerText = time;
    var sessionModal = new bootstrap.Modal(document.getElementById('sessionModal'), {
        keyboard: false
    });
    sessionModal.show();
}

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});