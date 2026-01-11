# src/security/security_app.py
import cv2
import os

from src.security.decoder import decoder_init, decoder_update, decoder_reset
from src.security.pattern_detector import detect_shape
from src.tracker.tracker_app import run_tracker_loop


def run_security_loop(cap):
    """
    Security loop.

    Returns True when the correct pattern sequence is detected.
    """
    # our code that we have to decode
    dec = decoder_init(
        target_sequence=["CIRCLE", "TRIANGLE", "SQUARE", "RECTANGLE"],
        hold_frames=7,
        timeout_sec=10.0
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        #the part of the camera that we will use to detect the patterns 
        roi_size = 320
        x1 = w // 2 - roi_size // 2
        y1 = h // 2 - roi_size // 2
        x2 = w // 2 + roi_size // 2
        y2 = h // 2 + roi_size // 2
        roi = frame[y1:y2, x1:x2]


        #here is the logic of the detection and the change of the state 
        shape_name, contour = detect_shape(roi, debug=True)
        state, input_seq, msg = decoder_update(dec, shape_name)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

        #UI
        if shape_name is not None and contour is not None:
            contour = contour + [x1, y1]
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)
            cv2.putText(frame, shape_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.putText(frame, "Show shape inside the box", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"STATE: {state}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"TARGET: {dec['target']}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"INPUT: {input_seq}", (10, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"MSG: {msg}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "r: reset | q: quit", (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Security - Pattern Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            decoder_reset(dec)
        if key == ord('q'):
            return False

        if state == "UNLOCKED":
            cv2.destroyWindow("Security - Pattern Detection")
            return True

    return False
