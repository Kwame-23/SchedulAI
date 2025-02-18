// Sample lecturer data (replace with database fetch later)
const lecturers = [
    { name: "Dr. John Doe", faculty: "Computer Science" },
    { name: "Prof. Jane Smith", faculty: "Mathematics" },
    { name: "Dr. Alex Johnson", faculty: "Physics" }
];

// Function to display lecturers
function displayLecturers() {
    const container = document.getElementById("lecturer-container");
    container.innerHTML = ""; // Clear container before re-adding
    lecturers.forEach((lecturer, index) => {
        const card = document.createElement("div");
        card.classList.add("lecturer-card");
        card.innerHTML = `
            <p><strong>${lecturer.name}</strong></p>
            <p>${lecturer.faculty}</p>
            <div class="button-group">
                <button class="edit-button" onclick="editLecturer(${index})">Edit</button>
                <button class="delete-button" onclick="deleteLecturer(${index})">Delete</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Function to add a new lecturer
function addLecturer() {
    const name = prompt("Enter Lecturer Name:");
    const faculty = prompt("Enter Faculty:");
    if (name && faculty) {
        lecturers.push({ name, faculty });
        displayLecturers();
    }
}

// Function to edit a lecturer
function editLecturer(index) {
    const newName = prompt("Edit Name:", lecturers[index].name);
    const newFaculty = prompt("Edit Faculty:", lecturers[index].faculty);
    if (newName && newFaculty) {
        lecturers[index] = { name: newName, faculty: newFaculty };
        displayLecturers();
    }
}

// Function to delete a lecturer
function deleteLecturer(index) {
    if (confirm("Are you sure you want to delete this lecturer?")) {
        lecturers.splice(index, 1);
        displayLecturers();
    }
}

// Display initial lecturers
displayLecturers();
