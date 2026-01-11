import cv2
import time

from src.tracker.base_detector import GreenBaseDetector
from src.hologram.renderer import HologramRenderer



def run_tracker_loop(cap):
    """
    Main tracker loop.

    - Detects the green base (position, size and angle)
    - Detects strong eye blinks
    - After 3 blinks, the system becomes ACTIVE
    - The hologram is rendered only when ACTIVE is True
    """
    # initialize base detector and hologram renderer
    detector = GreenBaseDetector()
    holo = HologramRenderer()



    prev_time= time.time()
    t = 0  

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # mirror image for a more natural interaction
        frame =cv2.flip(frame, 1)
        t += 1

        # detect green base in the frame
        det, _ =detector.detect(frame, debug=True)

        if det is not None:
            cx, cy = det["center"]
            ang = det["angle"]
            size = det["size"]

      

            # we display estimated base orientation
            cv2.putText(frame, f"Base angle: {-ang:.1f}",
            (int(cx), int(max(0, cy - 20))),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (0, 255, 255), 2)


            frame=holo.render(frame, (cx, cy), ang, size, t=t)

        #calculation of FPS
        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now

        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2)

        cv2.putText(frame, "TRACKER MODE | q: quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 2)

        
        cv2.imshow("Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

