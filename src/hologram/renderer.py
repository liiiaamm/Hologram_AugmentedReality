# src/hologram/renderer.py
import numpy as np
import cv2
from .effects import glow, scanlines, alpha_blend, flicker


class HologramRenderer:
    """
    This class handles the rendering of the hologram.
    It draws the hologram locally, applies rotation,
    and anchors it to the detected base on the camera frame.
    """

    def __init__(self):
        pass

    def _draw_holo_local(self, layer, t):
        """
        This function draws a procedural hologram on a local image layer.
        The hologram is asymmetric so rotation can be clearly perceived.

        :param layer: local hologram image
        :param t: time index used for animation effects
        :return: anchor point (ax, ay) of the hologram projector
        """
        h, w = layer.shape[:2]

        # Anchor position: horizontally centered and placed near the bottom
        # to represent the projector / base of the hologram
        cx, cy = w // 2, int(h * 0.70)

        # Base projector (anchor)
        cv2.circle(layer, (cx, cy), 8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.line(layer, (cx-20, cy+5), (cx+20, cy+5), (255,255,255), 1, cv2.LINE_AA)

        # Vertical column
        cv2.line(layer, (cx, cy), (cx, cy-140), (255, 255, 255), 1, cv2.LINE_AA)

        # Head (oval shape)
        cv2.ellipse(layer, (cx, cy-165), (22, 12), 0, 0, 360,
                    (255,255,255), 1, cv2.LINE_AA)

        # Asymmetric arms so rotation is visually evident
        cv2.line(layer, (cx, cy-120), (cx-60, cy-95),
                 (255,255,255), 1, cv2.LINE_AA)
        cv2.line(layer, (cx, cy-120), (cx+95, cy-80),
                 (255,255,255), 1, cv2.LINE_AA)
        cv2.circle(layer, (cx+95, cy-80), 3,
                   (255,255,255), -1, cv2.LINE_AA)

        # Fake volumetric effect: multiple slightly shifted copies
        # with decreasing intensity
        for k in range(1, 6):
            dy = k * 3
            a = 1.0 - k / 7.0
            tmp = np.zeros_like(layer)

            cv2.line(tmp, (cx, cy), (cx, cy-140),
                     (255,255,255), 1, cv2.LINE_AA)
            cv2.ellipse(tmp, (cx, cy-165-dy), (22, 12), 0, 0, 360,
                        (255,255,255), 1, cv2.LINE_AA)
            cv2.line(tmp, (cx, cy-120-dy), (cx-60, cy-95-dy),
                     (255,255,255), 1, cv2.LINE_AA)
            cv2.line(tmp, (cx, cy-120-dy), (cx+95, cy-80-dy),
                     (255,255,255), 1, cv2.LINE_AA)

            # Blend each layer to simulate depth
            layer[:] = cv2.addWeighted(layer, 1.0, tmp, 0.18 * a, 0)

        # Particles with temporal flickering
        rng = (t * 1664525 + 1013904223) & 0xFFFFFFFF
        for i in range(120):
            rng = (rng * 1664525 + 1013904223) & 0xFFFFFFFF
            x = int(rng % w)
            rng = (rng * 1664525 + 1013904223) & 0xFFFFFFFF
            y = int(rng % int(h * 0.85))

            if (i + t) % 7 == 0:
                cv2.circle(layer, (x, y), 1,
                           (255,255,255), -1, cv2.LINE_AA)

        # Return the anchor (projector center)
        return (cx, cy)

    def render(self, frame_bgr, base_center, base_angle_deg, base_size_wh, t=0):
        """
        This function renders the hologram on top of the camera frame.
        It applies effects, rotation, anchoring and blending.

        :param frame_bgr: camera frame image
        :param base_center: detected center of the base
        :param base_angle_deg: detected base rotation angle
        :param base_size_wh: detected base size (width, height)
        :param t: time index
        :return: frame with the hologram rendered
        """

        H,W = frame_bgr.shape[:2]
        cx,cy = base_center
        bw,bh = base_size_wh

        #local hologram canvas size based on the detected base size
        side =int(max(260, max(bw, bh)))
        layer =np.zeros((side, side, 3), dtype=np.uint8)

        #draw local hologram and get anchor
        ax, ay = self._draw_holo_local(layer, t)

        #apply hologram effects
        layer = glow(layer, sigma=7.0, gain=0.9)
        layer = scanlines(layer, period=4, strength=0.22)

        #here we rotate the full hologram layer around its center
        M =cv2.getRotationMatrix2D((side / 2, side / 2),
                                    -base_angle_deg, 1.0)
        #then we obtain the image rotated 
        rotated =cv2.warpAffine(
            layer,M, (side, side),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT
        )

        # finally we calculate anchor position after rotation
        p = np.array([ax, ay,1], dtype=np.float32)
        rax, ray = (M@ p).tolist()

        #place the rotated hologram so the anchor matches the base center (we do this because cv2 start the image in the upper left corner at a (0,0) position)
        x1 = int(cx- rax)
        y1 = int(cy -ray)
        x2 = x1 +side
        y2 = y1 +side

        # clip hologram region to the camera frame
        sx1 = max(0, x1); sy1 = max(0, y1)
        sx2 = min(W, x2); sy2 = min(H, y2)

        # ff there is no visible intersection, return the original frame
        if sx1 >= sx2 or sy1 >= sy2:
            return frame_bgr
        #calculate corresponding region inside hologram
        rx1 = sx1 -x1
        ry1 = sy1- y1
        rx2 = rx1+ (sx2- sx1)
        ry2 = ry1 + (sy2- sy1)
        #xtract regions of interest
        roi_frame = frame_bgr[sy1:sy2, sx1:sx2]
        roi_holo  = rotated[ry1:ry2, rx1:rx2]
        # blend hologram and frame with flickering transparency
        a =flicker(0.60, t, jitter=0.10)
        frame_bgr[sy1:sy2, sx1:sx2] = alpha_blend(roi_frame, roi_holo, a)

        return frame_bgr
