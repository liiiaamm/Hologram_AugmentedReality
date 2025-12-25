import cv2
import os

save_dir = "data/calibration/laptop/images"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    os._exit(0)

img_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break

    # Keep the same flip you decided to use
    frame = cv2.flip(frame, 1)

    cv2.imshow("Capture Calibration Images", frame)

    key = cv2.waitKey(1) & 0xFF

    # Press 'c' to capture
    if key == ord('c'):
        filename = os.path.join(save_dir, f"img_{img_id:03d}.png")
        cv2.imwrite(filename, frame)
        print("Saved:", filename)
        img_id += 1

    # Press 'q' to quit
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
