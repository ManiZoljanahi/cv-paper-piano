""" This script is a diagnostic tool to verify that the webcam is working and accessible by OpenCV before running the main application. """

import cv2

# Prints status messages ("Initializing...", "Attempting to open Camera 0...").
def check_cam():
    print("Initializing Camera Test...")
    print("Attempting to open Camera Index 0...")

    # Tries to open the default camera (Index 0).
    # cv2.CAP_DSHOW is a flag specifically for Windows (DirectShow) to make the camera start up faster.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Checks if the camera failed to initialize.
    # If failed, it prints an error and attempts to open Index 1
    if not cap.isOpened():
        print("Error: Could not open Camera 0.")
        print("Attempting to open Camera Index 1...")
        cap = cv2.VideoCapture(1)

        # If Index 1 also fails (if not cap.isOpened()), it prints "FATAL ERROR" and returns (exits the function).
        if not cap.isOpened():
            print("FATAL ERROR: No cameras found.")
            return

    # Prints "Success" and instructions to press 'q'
    print("Success: Camera opened.")
    print("Press 'q' to quit.")

    # Starts an infinite loop to process video frames.
    while True:

        # Reads a single frame. ret is a boolean (True if successful), frame is the image data.
        ret, frame = cap.read()

        # If reading failed (e.g., camera disconnected), it breaks the loop.
        if not ret:
            print("Error: Failed to read frame.")
            break

        # Opens a window titled "Camera Test" showing the current frame.
        cv2.imshow("Camera Test (Press q to quit)", frame)

        # Waits 1 millisecond for a key press. If the 'q' key is pressed, it breaks the loop.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Frees the camera hardware so other apps can use it.
    cap.release()

    # Closes the video window.
    cv2.destroyAllWindows()

# Ensures the function only runs if the file is executed directly.
if __name__ == "__main__":
    check_cam()
