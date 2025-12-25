import cv2
import numpy as np
import glob
import os

# Chessboard configuration
board_size = (9, 6)        # internal corners
square_size = 0.029       # meters (25 mm)

# Path to calibration images
image_path = "data/calibration/laptop/images/*.png"
images = glob.glob(image_path)

if len(images) == 0:
    print("Error: No calibration images found")
    os._exit(0)

# Prepare object points (0,0,0), (1,0,0), ...
objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []  # 3D points
imgpoints = []  # 2D points

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, board_size, None)

    if ret:
        corners = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        objpoints.append(objp)
        imgpoints.append(corners)
    else:
        print("Chessboard not detected in:", fname)

# Camera calibration
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("RMS reprojection error:", ret)
print("Camera matrix:\n", K)
print("Distortion coefficients:\n", dist)

# Save results
output_file = "data/calibration/laptop/intrinsics.yaml"
fs = cv2.FileStorage(output_file, cv2.FILE_STORAGE_WRITE)
fs.write("K", K)
fs.write("dist", dist)
fs.write("RMS", ret)
fs.release()

print("Calibration saved to:", output_file)
