import cv2
import numpy as np

def _touches_border(cnt, w, h, margin=2):
    x, y, cw, ch = cv2.boundingRect(cnt)
    return (x <= margin or y <= margin or (x + cw) >= (w - margin) or (y + ch) >= (h - margin))

def detect_shape(image, debug=False):
    h, w = image.shape[:2]
    roi_area = w * h

    # clahe applied to enhance local contrast and improve feature visibility.
    # we decided to apply clahe and not global histogram because there is no homogeneous lightning
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # done to remove noise before applying thresholds 
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # adaptative instead of global because heterogeneous lightning 
    th = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,  
        4   
    )


    # we use 2 rectangles kernels, one smaller and one bigger 
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))


    # we apply the smaller kernel to the opening part because we have already removed most of the noise with the blur, so, in order not to damage the
    # structure, we apply an smaller kernel one iteration
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel3, iterations=1)
    # after applying the opening part, we apply two iterations for the closing part with a bigger kernel in order to join strokes caused by the physical or 
    # the threshold part 
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel5, iterations=2)
    # we finally dilate the figure a little bit in order to obtain noteicable strokes 
    th = cv2.dilate(th, kernel3, iterations=1)

    if debug:
        cv2.imshow("debug_th", th)

    # we try to find solid contours by using RETR_EXTERNAL in order to obtain just external contours and  CHAIN_APPROX_SIMPLE to not obtain reduntant points 
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None

    #We then filter our candidates
    candidates = []
    for c in contours:
        # calculate the area 
        area = cv2.contourArea(c)
        if area < 1200:           
            continue #we discard small contours (normally noise)
        if area > 0.90 * roi_area:  # if the object size is approximately the ROI, it is discarded to avoid capturing folios.
            continue
        if _touches_border(c, w, h, margin=2):
            continue
        candidates.append(c)

    if not candidates:
        return None, None

#select the largest candidate contour, which is most likely the drawn shape
    contour = max(candidates, key=cv2.contourArea)

    #compute the perimeter of the selected contour
    peri = cv2.arcLength(contour, True)
    if peri == 0:
        return None, None

    #approximate the contour to a polygon to reduce noise and count vertices
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    vertices = len(approx)

    #compute area and circularity for shape classification
    area = cv2.contourArea(contour)
    circularity = 4 * np.pi * area / (peri * peri)

    shape = None

    #triangle detection: 3 vertices after polygon approximation
    if vertices == 3:
        shape = "TRIANGLE"

    #quadrilateral case: square or rectangle
    elif vertices == 4:
        #bounding box of the approximated contour
        x, y, bw, bh = cv2.boundingRect(approx)

        #aspect ratio to distinguish square vs rectangle
        ar = bw / float(bh)

        #extent measures how well the contour fills its bounding box
        rect_area = bw * bh
        extent = area / float(rect_area) if rect_area > 0 else 0

        #square: aspect ratio close to 1 and good filling
        if 0.90 <= ar <= 1.10 and extent > 0.55:
            shape = "SQUARE"
        #rectangle: four sides but aspect ratio not close to 1
        elif extent > 0.45:
            shape = "RECTANGLE"

    else:
        #circularity close to 1 indicates a circular shape
        if circularity > 0.82:
            shape = "CIRCLE"

    #return detected shape name and its contour
    return shape, contour