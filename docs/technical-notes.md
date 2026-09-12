> Original team documentation. Historical performance figures below have not been independently reproduced in this portfolio update. Use the root README for verified demo instructions.

# Holographic Projection System with Pattern-Based Authentication

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)

An interactive computer vision system combining security through pattern recognition with real-time holographic projection. Developed as the final project for Computer Vision I course.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Overview

This project implements a modular computer vision system with three main components:

1. **Camera Calibration Module**: Offline calibration using Zhang's method with a chessboard pattern to correct lens distortions.

2. **Security Module**: Pattern recognition system that authenticates users through detection and validation of a specific sequence of four geometric shapes (circle, triangle, square, rectangle).

3. **Tracking and Hologram Module**: Real-time detection of a green elongated base with orientation estimation using PCA, followed by procedural hologram rendering with visual effects.

The system demonstrates practical application of classical computer vision techniques including adaptive image processing, morphological operations, color segmentation, geometric analysis, and image composition.

---

## Features

- Camera calibration with automatic distortion correction
- Robust geometric shape detection (circles, triangles, squares, rectangles)
- Sequential pattern validation with finite state machine
- Real-time green base tracking with orientation estimation
- Procedural 3D hologram rendering with visual effects
- Performance optimized for real-time execution (20-30 FPS)

---

## System Architecture

```
┌─────────────┐
│   Camera    │ ──► BGR Frame
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Calibration │ ──► Distortion Correction
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Security   │ ──► Pattern Detection + Decoder
└──────┬──────┘
       │ (UNLOCKED)
       ▼
┌─────────────┐
│   Tracker   │ ──► Green Base Detection + PCA
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Hologram   │ ──► Rendering + Visual Effects
└─────────────┘
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Functional webcam
- Operating System: Windows, macOS, or Linux


### Requirements

```txt
numpy>=1.21.0
opencv-python>=4.5.0
opencv-contrib-python>=4.5.0
```

---

## Usage

### Step 1: Camera Calibration (Required - First Time Only)

The calibration process must be completed before running the main system.

#### 1.1 Capture Calibration Images

```bash
python -m src.calibration.capture_images
```

**Instructions**:
- Capture 15-20 images showing the pattern from different angles and distances
- Press `c` to capture an image
- Press `q` to finish capturing

#### 1.2 Perform Calibration

```bash
python -m src.calibration.calibrate
```

This will compute the camera intrinsic parameters and distortion coefficients, saving them to `data/calibration/laptop/intrinsics.yaml`.

#### 1.3 Verify Calibration (Optional)

```bash
python -m src.calibration.undisort_live
```

This displays the real-time undistorted camera feed to verify calibration quality.

### Step 2: Run Main System

```bash
python -m src.main
```

### Step 3: Interaction Protocol

#### Security Phase

1. Draw the following shapes on white paper using black ink
2. Present each shape inside the yellow ROI box in the following order:
   - Circle
   - Triangle
   - Square
   - Rectangle
3. Hold each shape stable for approximately 1-2 seconds
4. The system requires 5 consecutive stable detections before registering a shape
5. Press `r` to reset the sequence if an error occurs
6. The system automatically unlocks after correct sequence completion

#### Hologram Phase

1. Place the green base (cardboard or paper) in front of the camera
2. The hologram will appear projected on the base
3. Move and rotate the base to observe the hologram tracking behavior
4. Press `q` to exit the application

---

## Project Structure

```
hologram-pattern-detection/
│
├── main.py                      # Main entry point
│
├── calibration/                 # Calibration module
│   ├── capture_images.py       # Image capture script
│   ├── calibrate.py            # Calibration process
│   └── test_undistort.py       # Verification script
│
├── src/
│   ├── security/               # Security system
│   │   ├── security_app.py    # Main security loop
│   │   ├── pattern_detector.py # Shape detection
│   │   └── decoder.py         # Sequence decoder
│   │
│   ├── tracker/                # Tracking system
│   │   ├── tracker_app.py     # Main tracking loop
│   │   └── base_detector.py   # Green base detector
│   │
│   └── hologram/               # Hologram system
│       ├── renderer.py        # Main renderer
│       ├── effects.py         # Visual effects
│       └── wireframe.py       # Humanoid 3D model
│
├── data/
│   └── calibration/            # Calibration data
│       └── laptop/
│           ├── images/         # Captured images
│           └── intrinsics.yaml # Camera parameters

```

---

## Technical Details

### Camera Calibration

**Method**: Zhang's calibration technique using a planar chessboard pattern (9×6 internal corners, 29mm square size).

**Process**:
1. Automatic corner detection using `cv2.findChessboardCorners()`
2. Subpixel refinement with `cv2.cornerSubPix()`
3. Camera matrix and distortion coefficient estimation via `cv2.calibrateCamera()`
4. Real-time distortion correction using `cv2.undistort()`

**Typical RMS Error**: < 0.7 pixels

### Pattern Detection

**Image Processing Pipeline**:
```
BGR Frame → Grayscale → CLAHE → Gaussian Blur →
Adaptive Threshold → Opening → Closing → Dilation →
Contour Detection → Geometric Filtering → Classification
```

**Preprocessing Techniques**:
- **CLAHE** (Contrast Limited Adaptive Histogram Equalization): Improves local contrast under heterogeneous illumination
- **Gaussian Blur** (5×5 kernel): Reduces high-frequency noise
- **Adaptive Thresholding**: Local threshold computation for robust segmentation under variable lighting

**Morphological Operations**:
- **Opening** (3×3 kernel, 1 iteration): Removes isolated noise
- **Closing** (5×5 kernel, 2 iterations): Connects fragmented strokes
- **Dilation** (3×3 kernel, 1 iteration): Thickens contours

**Shape Classification Criteria**:

| Shape     | Vertices | Circularity | Aspect Ratio | Extent |
|-----------|----------|-------------|--------------|--------|
| Triangle  | 3        | -           | -            | -      |
| Square    | 4        | -           | 0.90-1.10    | >0.55  |
| Rectangle | 4        | -           | ≠1.0         | >0.45  |
| Circle    | >4       | >0.82       | -            | -      |

Where:
- **Circularity**: 4πA/P²
- **Aspect Ratio**: width/height of bounding rectangle
- **Extent**: contour area / bounding box area

### Sequential Decoder

**State Machine**:
- States: LOCKED (initial), UNLOCKED (authenticated)
- Target sequence: ["CIRCLE", "TRIANGLE", "SQUARE", "RECTANGLE"]

**Transition Rules**:
1. Shape must be stable for 5 consecutive frames before registration
2. Sequence is validated as a valid prefix after each addition
3. Invalid prefix triggers immediate reset
4. Timeout of 10 seconds without detection triggers reset
5. Complete sequence transitions to UNLOCKED state

### Green Base Tracking

**Color Segmentation**:
- Color space: HSV (Hue, Saturation, Value)
- Green range: H∈[40,90], S∈[35,255], V∈[25,255]
- Morphological refinement: Opening (1 iter.) + Closing (3 iter.)

**Candidate Evaluation Criteria**:
- Minimum area: 2% of frame area
- Aspect ratio: 2.0 to 15.0 (elongated shape)
- Fill ratio: >0.55 (coverage of minimum bounding rectangle)
- Solidity: >0.75 (area/convex hull area)

**Selection**: Candidate with maximum score = area × fill × solidity

**Orientation Estimation**:
- Method: Principal Component Analysis (PCA)
- First eigenvector indicates dominant direction
- Angle computation: θ = arctan2(vy, vx)

### Hologram Rendering

**Design**:
- Procedural humanoid wireframe with asymmetric arms
- Anchor point representing hologram projector
- Volumetric effect: 5 vertically displaced copies with decreasing transparency

**Visual Effects**:
1. **Glow**: Gaussian blur (σ=7) blended with original image
2. **Scanlines**: Periodic attenuation every 4 lines
3. **Flicker**: Temporal alpha variation with pseudorandom jitter

**Geometric Transformation**:
- Rotation matrix applied around hologram center
- Anchor point alignment with base center in global coordinates
- Clipping to frame boundaries

**Composition**:
- Alpha blending with camera frame (α ≈ 0.6)
- Temporal alpha modulation for flicker effect

---

## Performance

### Metrics

| Metric                    | Value       |
|---------------------------|-------------|
| Frame Rate (Security)     | 25-30 FPS   |
| Frame Rate (Tracking)     | 20-30 FPS   |
| Detection Accuracy        | ~95%        |
| Calibration RMS Error     | <0.7 px     |
| Detection Latency         | ~150ms      |
| Calibration Time          | 2-3 min     |


### Optimization

- ROI-based processing reduces computational load
- Morphological operations use small kernels for efficiency
- Contour filtering eliminates unnecessary processing
- Real-time performance maintained through algorithmic optimization

---

## Configuration

### Pattern Detector Parameters

Edit `src/security/pattern_detector.py`:

```python
# Gaussian blur kernel size
gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Increase for noisier conditions

# Adaptive threshold parameters
th = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    31,  # blockSize (must be odd)
    4    # C constant (adjust if detection fails)
)
```

### Green Base Detector Parameters

Edit `src/tracker/base_detector.py`:

```python
# HSV color range for green detection
hsv_lower=(40, 35, 25)   # H, S, V minimum values
hsv_upper=(90, 255, 255) # H, S, V maximum values

# Geometric constraints
min_area_ratio=0.02      # Minimum area (fraction of frame)
min_aspect=2.0           # Minimum elongation
max_aspect=15.0          # Maximum elongation
min_fill=0.55            # Minimum fill ratio
min_solidity=0.75        # Minimum solidity
```

### Camera Resolution

Edit `main.py`:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

## Troubleshooting

### Shape Detection Issues

**Problem**: Shapes are not detected consistently

**Solutions**:
- Ensure high contrast between ink and paper (black on white recommended)
- Draw shapes with clear, continuous edges
- Position paper in well-lit area without strong shadows
- Hold shape stable within yellow ROI box
- Increase Gaussian blur kernel size if environment is noisy
- Adjust adaptive threshold constant C parameter

### Green Base Detection Issues

**Problem**: Green base is not detected or tracking is unstable

**Solutions**:
- Use bright green cardboard or paper
- Ensure uniform lighting without direct shadows
- Adjust HSV range parameters to match your material
- Verify base aspect ratio is between 2.0 and 15.0
- Remove other green objects from background
- Increase base size if tracking is jittery

### Calibration Errors

**Problem**: High RMS error or calibration fails

**Solutions**:
- Capture at least 15 images of the chessboard pattern
- Cover different regions of the camera field of view
- Ensure chessboard is completely visible in all images
- Avoid motion blur by keeping pattern stationary during capture
- Verify pattern dimensions match code parameters (9×6 corners, 29mm squares)
- Use higher quality print of calibration pattern



---

## References

1. Zhang, Z. (2000). "A flexible new technique for camera calibration". IEEE Transactions on Pattern Analysis and Machine Intelligence, 22(11), 1330-1334.

2. Class Slides

5. OpenCV Documentation. Camera Calibration and 3D Reconstruction. Retrieved from https://docs.opencv.org/

---


## Authors

**[Liam Esgueva, Sergio Fernandez]**  
Universidad Pontificia Comillas, ICAI  
Mathematical Engineering  
Computer Vision I - Academic Year 2025/26

---

## Acknowledgments

This project was developed as part of the Computer Vision I course at Universidad Pontificia Comillas (ICAI). We acknowledge the course instructors for their guidance and the OpenCV community for their comprehensive documentation and resources.