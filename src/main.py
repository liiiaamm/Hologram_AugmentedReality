import cv2
import os

from src.security.security_app import run_security_loop
from src.tracker.tracker_app import run_tracker_loop


def main():
    """
    Project entry point.

    - Runs security module first
    - If unlocked, runs tracker module
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    unlocked = run_security_loop(cap)

    if unlocked:
        run_tracker_loop(cap)

    cap.release()
    cv2.destroyAllWindows()
    os._exit(0)


if __name__ == "__main__":
    main()
