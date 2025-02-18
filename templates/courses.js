// Function to get courses from localStorage or use default data
function getCourses() {
    const storedCourses = localStorage.getItem("courses");
    return storedCourses ? JSON.parse(storedCourses) : [];
}

// Load courses
let courses = getCourses();
let editIndex = null; // Track the course being edited

// Function to update localStorage
function updateLocalStorage() {
    localStorage.setItem("courses", JSON.stringify(courses));
}

// Function to display courses
function displayCourses() {
    const container = document.getElementById("course-container");
    container.innerHTML = ""; 

    if (courses.length === 0) {
        container.innerHTML = `<p>No courses available. Add a new course.</p>`;
        return;
    }

    courses.forEach((course, index) => {
        const card = document.createElement("div");
        card.classList.add("course-card");
        card.innerHTML = `
            <p><strong>Code:</strong> ${course.CourseCode}</p>
            <p><strong>Name:</strong> ${course.CourseName}</p>
            <p><strong>Requirement:</strong> ${course.RequirementType}</p>
            <p><strong>Active:</strong> ${course.ActiveFlag === "1" ? "Yes" : "No"}</p>
            <p><strong>Credits:</strong> ${course.Credits}</p>
            <div class="button-group">
                <button class="edit-button" onclick="openForm(${index})">Edit</button>
                <button class="delete-button" onclick="deleteCourse(${index})">Delete</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Function to open the modal form for adding/editing
function openForm(index = null) {
    document.getElementById("courseForm").style.display = "block";
    editIndex = index;

    if (index !== null) {
        document.getElementById("form-title").innerText = "Edit Course";
        document.getElementById("courseCode").value = courses[index].CourseCode;
        document.getElementById("courseName").value = courses[index].CourseName;
        document.getElementById("requirementType").value = courses[index].RequirementType;
        document.getElementById("activeFlag").value = courses[index].ActiveFlag;
        document.getElementById("credits").value = courses[index].Credits;
    } else {
        document.getElementById("form-title").innerText = "Add Course";
        document.getElementById("courseCode").value = "";
        document.getElementById("courseName").value = "";
        document.getElementById("requirementType").value = "";
        document.getElementById("activeFlag").value = "1";
        document.getElementById("credits").value = "";
    }
}

// Function to close the modal
function closeForm() {
    document.getElementById("courseForm").style.display = "none";
}

// Function to save course (FIXED)
function saveCourse() {
    const courseCode = document.getElementById("courseCode").value.trim();
    const courseName = document.getElementById("courseName").value.trim();
    const requirementType = document.getElementById("requirementType").value.trim();
    const activeFlag = document.getElementById("activeFlag").value;
    const credits = parseFloat(document.getElementById("credits").value);

    if (!courseCode || !courseName || !requirementType || isNaN(credits)) {
        alert("Please fill in all fields correctly.");
        return;
    }

    const newCourse = { CourseCode: courseCode, CourseName: courseName, RequirementType: requirementType, ActiveFlag: activeFlag, Credits: credits };

    if (editIndex !== null) {
        courses[editIndex] = newCourse;
    } else {
        courses.push(newCourse);
    }

    updateLocalStorage();
    displayCourses();
    closeForm();
}

// Function to delete a course
function deleteCourse(index) {
    if (confirm("Are you sure you want to delete this course?")) {
        courses.splice(index, 1);
        updateLocalStorage();
        displayCourses();
    }
}

// Load courses on page load
window.onload = displayCourses;
