// Function to get rooms from localStorage or use default data
function getRooms() {
    const storedRooms = localStorage.getItem("rooms");
    return storedRooms ? JSON.parse(storedRooms) : [
        { Location: "Apt Hall 216", Capacity: "74" },
        { Location: "Apt Hall 217", Capacity: "75" },
        { Location: "Fab Lab 202", Capacity: "72" }
    ];
}

// Load rooms
let rooms = getRooms();
let editIndex = null; // Track the room being edited

// Function to update localStorage
function updateLocalStorage() {
    localStorage.setItem("rooms", JSON.stringify(rooms));
}

// Function to display rooms
function displayRooms() {
    const container = document.getElementById("room-container");
    if (!container) {
        console.error("Room container not found!");
        return;
    }

    container.innerHTML = ""; // Clear container before re-adding
    if (rooms.length === 0) {
        container.innerHTML = `<p>No rooms available. Add a new room.</p>`;
        return;
    }

    rooms.forEach((room, index) => {
        const card = document.createElement("div");
        card.classList.add("room-card");
        card.innerHTML = `
            <p><strong>Location:</strong> ${room.Location}</p>
            <p><strong>Capacity:</strong> ${room.Capacity}</p>
            <div class="button-group">
                <button class="edit-button" onclick="openForm(${index})">Edit</button>
                <button class="delete-button" onclick="deleteRoom(${index})">Delete</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Function to open the modal form (for add/edit)
function openForm(index = null) {
    document.getElementById("roomForm").style.display = "block";
    editIndex = index; // Track index for editing

    if (index !== null) {
        // If editing, pre-fill form
        document.getElementById("form-title").innerText = "Edit Room";
        document.getElementById("roomLocation").value = rooms[index].Location;
        document.getElementById("roomCapacity").value = rooms[index].Capacity;
    } else {
        // If adding, reset form
        document.getElementById("form-title").innerText = "Add Room";
        document.getElementById("roomLocation").value = "";
        document.getElementById("roomCapacity").value = "";
    }
}

// Function to close the modal form
function closeForm() {
    document.getElementById("roomForm").style.display = "none";
}

// Function to add or edit a room
function saveRoom() {
    const location = document.getElementById("roomLocation").value.trim();
    let capacity = document.getElementById("roomCapacity").value.trim();

    if (!location || !capacity) {
        alert("Both fields are required!");
        return;
    }

    capacity = parseInt(capacity);
    if (isNaN(capacity) || capacity <= 0) {
        alert("Capacity must be a valid positive number.");
        return;
    }

    if (editIndex !== null) {
        // Edit existing room
        rooms[editIndex] = { Location: location, Capacity: capacity };
    } else {
        // Add new room
        rooms.push({ Location: location, Capacity: capacity });
    }

    updateLocalStorage();
    displayRooms();
    closeForm();
}

// Function to delete a room
function deleteRoom(index) {
    if (confirm("Are you sure you want to delete this room?")) {
        rooms.splice(index, 1);
        updateLocalStorage();
        displayRooms();
    }
}

// Ensure rooms are displayed when the page loads
window.onload = function () {
    rooms = getRooms(); // Reload rooms
    displayRooms();
};
