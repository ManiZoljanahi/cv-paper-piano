/** The JavaScript code bridging Python and HTML. */

// Gets references to HTML elements by ID.
const noteDisplay = document.getElementById('note-display');
const fullNoteName = document.getElementById('full-note-name');
const historyList = document.getElementById('history-list');
const cameraFeed = document.getElementById('video-feed');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

// Update Video Feed
// Receives a Base64 string from Python and sets it as the src of the image tag, creating a video stream effect.
function updateFrame(base64Image) {
    if(cameraFeed) {
        cameraFeed.src = "data:image/jpeg;base64," + base64Image;
    }
}

// Update Status (Green/Red Dot)
// Receives a Base64 string from Python and sets it as the src of the image tag, creating a video stream effect.
function updateStatus(msg, isError) {
    if(statusText) statusText.innerText = msg;
    if(statusDot) {
        statusDot.style.background = isError ? "red" : "#00d26a";
    }
}

// Handle Note Hit (Received from Python as "C4", "A#0", etc.)
function highlightNoteString(noteName) {
    console.log("Playing:", noteName);

    // Regex matches the letter/accidental and the number
    // match(/([A-G]#?)(\d)/) splits "C#4" into "C#" and "4".
    const match = noteName.match(/([A-G]#?)(\d)/);
    let displayNote = noteName;
    let displayOctave = "";
    if (match) {
        displayNote = match[1];
        displayOctave = match[2];
    }

    // Updates the large text on display.
    if(noteDisplay) noteDisplay.innerText = displayNote;
    if(fullNoteName) fullNoteName.innerText = "Octave " + displayOctave;

    // Add to History: Creates a new div, prepends it to the list, and removes old items if length > 10.
    if(historyList) {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerText = noteName;
        historyList.prepend(item);
        if (historyList.children.length > 10) {
            historyList.lastElementChild.remove();
        }
    }

    // Visual Key Highlight on Screen (Optional, if you have divs with IDs)
    // Tries to find an element with the ID of the note (optional feature) to add an .active CSS class.
    const keyElement = document.getElementById(noteName) || document.getElementById("key-" + noteName);
    if (keyElement) {
        keyElement.classList.add('active');
        setTimeout(() => keyElement.classList.remove('active'), 200);
    }
}

// Signals Python that UI is ready to start the camera. This prevents the "Camera starts before UI exists" crash.
window.addEventListener('pywebviewready', function() {
    console.log("UI Ready. Signaling Python...");
    pywebview.api.signal_ui_ready();
});