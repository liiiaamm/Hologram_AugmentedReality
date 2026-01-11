import cv2
import numpy as np


def _contour_angle_pca(cnt) -> float:
    """
    This function estimates the orientation of a contour using PCA.

    :param cnt: contour points
    :return: angle of the dominant direction in degrees
    """
    #we transform the cnt array into a list of (x, y) points
    #in order to apply PCA to the contour
    pts =cnt.reshape(-1, 2).astype(np.float32)

    #PCA gives the principal directions of the point cloud
    mean,eigenvectors, _ =cv2.PCACompute2(pts, mean=None)

    #he first eigenvector corresponds to the dominant direction
    v= eigenvectors[0]

    #ensure a consistent direction to avoid angle sign ambiguity
    if v[0] <0:
        v =-v

    #calcualte the angle of the vector using arctan
    return float(np.degrees(np.arctan2(v[1], v[0])))


class GreenBaseDetector:
    """
    This class detects a green elongated base in the camera frame.
    It estimates its position, size and orientation to be used
    by the hologram renderer.
    """

    def __init__(
        self,
        #we use HSV instead of RGB to reduce sensitivity to lighting changes
        #these values are commonly used to detect green while avoiding shadows
        hsv_lower=(40,  35, 25),
        hsv_upper=(90, 255, 255),

        #contours smaller than this ratio of the image are considered noise
        min_area_ratio=0.02,


        #geometric constraints defining a valid base shape
        min_fill= 0.55,           # how much the contour fills its bounding rectangle
        min_solidity=0.75,       # contour area / convex hull area
        min_aspect=2.0,          # elongated shape
        max_aspect=15.0,

        #optional vertical region of interest (as image proportions)
        roi_ymin =0.20,
        roi_ymax=0.95
    ):
        # convert HSV bounds to numpy arrays for inRange
        self.lower = np.array(hsv_lower, dtype=np.uint8)
        self.upper = np.array(hsv_upper, dtype=np.uint8)

        self.min_area_ratio = float(min_area_ratio)

        self.min_fill = float(min_fill)
        self.min_solidity = float(min_solidity)
        self.min_aspect = float(min_aspect)
        self.max_aspect = float(max_aspect)

        self.roi_ymin = float(roi_ymin)
        self.roi_ymax = float(roi_ymax)


    def detect(self, frame_bgr, debug=False):
        """
        This function detects the green base in the input frame.

        :param frame_bgr: input camera frame
        :param debug: if True, returns the segmentation mask
        :return: detection dictionary and optional debug mask
        """
        H, W = frame_bgr.shape[:2]

        #limit the search region vertically to  avoid false positives
        y0 = int(self.roi_ymin * H)
        y1 =int(self.roi_ymax * H)
        crop = frame_bgr[y0:y1, :]

        #convert to HSV and segment green color
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        mask= cv2.inRange(hsv, self.lower, self.upper)

        #create an elliptical kernel to better match shapes
        k =cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        #remove small isolated noise pixels from the mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k, iterations=1)
        #fill small gaps and holes inside the detected base
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=3)

        if debug:
            cv2.imshow("mask", mask)

        #find xternal contour in the mask
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None, (mask if debug else None)

        #sort contours by area so we can obtain the biggest area 
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        #we instantiate the min area to then compare it with the contour's area 
        min_area = self.min_area_ratio * (H * W)

        #handle the scores by multiplying al the values comparing values (like solidity, area, aspect...)
        best = None
        best_score = -1.0

        #evaluate only the largest candidates to reduce noise
        for cnt in contours[:8]:
            #our first check is with the area in order to eliminate noise 
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            
            # minimum area rectangle 
            rect = cv2.minAreaRect(cnt)
            (rcx, rcy), (rw, rh), _ = rect
            rw, rh = float(rw), float(rh)
            #then we check how much is pur shape elongated 
            aspect = max(rw, rh) / max(1e-6, min(rw, rh))
            if not (self.min_aspect <= aspect <= self.max_aspect):
                continue

            #after that we check how much does the area of the contour fill in a rectangle 
            rect_area = rw * rh
            fill = float(area / max(1e-6, rect_area))
            if fill < self.min_fill:
                continue

            #we finally calculate the opacity of our contour using computacional geometric concepts (calculate the area of its convex hull and compare it with the its area)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(area / max(1e-6, hull_area))
            if solidity < self.min_solidity:
                continue

            #score combining area and geometric quality
            score = area * fill * solidity
            if score > best_score:
                best_score = score
                best = (cnt, rect, area, fill, solidity, aspect)
            # we obtain the best score 

        if best is None:
            return None, (mask if debug else None)

        cnt, rect, area, fill, solidity, aspect = best

        # then we convert contour coordinates back to global image coordinates
        cnt_global = cnt.copy()
        cnt_global[:, 0, 1] += y0

        #center and size from minimum area rectangle 
        (rcx, rcy), (rw, rh), _ = rect
        cx = rcx
        cy = rcy + y0

        # orientation estimation using PCA
        angle = _contour_angle_pca(cnt_global)

        return {
            "center": (float(cx), float(cy)),
            "size": (float(rw), float(rh)),
            "angle": float(angle),
        }, None

