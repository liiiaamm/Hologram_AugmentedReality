import cv2
import os

# Load calibration
fs = cv2.FileStorage("data/calibration/laptop/intrinsics.yaml", cv2.FILE_STORAGE_READ)
K = fs.getNode("K").mat()
dist = fs.getNode("dist").mat()
fs.release()

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    os._exit(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break

    # Keep same flip used during calibration
    frame = cv2.flip(frame, 1)

    # Undistort
    undistorted = cv2.undistort(frame, K, dist)

    cv2.imshow("Undistorted Camera", undistorted)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
