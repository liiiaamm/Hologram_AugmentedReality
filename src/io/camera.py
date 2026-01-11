import cv2
import os

# Open the laptop camera 
cap = cv2.VideoCapture(0)

# Check if the camera opened correctly
if not cap.isOpened():
    print("Error: Could not open camera")
    os._exit(0)

# Read camera properties (same idea as Part C)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

print("Camera resolution:", frame_width, "x", frame_height)
print("Camera FPS:", fps)

# Read frames in a loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break
    
    frame = cv2.flip(frame, 1)
    


    cv2.imshow("Camera", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


