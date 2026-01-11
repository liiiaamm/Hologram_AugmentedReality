import numpy as np
import cv2

def glow(layer, sigma=6.0, gain=0.8):
    """
    To give volume and a sense of 3d to the hologram, applied to the lines that describe it 
    
    :param layer: image 
    :param sigma: controls how much dos the halo extends
    :param gain: describe the intensity of this halo
    """
    blur = cv2.GaussianBlur(layer, (0,0), sigmaX=sigma, sigmaY=sigma)
     # we sum the thow images to give to the original image an "halo" (original + k*blurred) -> the orignal lines stay the same and the pixels around them get grisaceous colors 
    return cv2.addWeighted(layer, 1.0, blur, gain, 0)

def scanlines(layer, period=4, strength=0.25):
    """
    This gives the hologram a non-uniform texture to get a realistic appearance 
    
    :param layer: image
    :param period: effect per number of lines 
    :param strength: how much does the image darkens 
    """
    out = layer.copy()
    H = out.shape[0]
    for y in range(0, H, period):
        out[y:y+1] = (out[y:y+1] * (1.0 - strength)).astype(out.dtype)
    return out


def alpha_blend(dst, src, alpha): 
    """
    this function mixes the hologram with the camera frame using transparency so both remain visible.
    
    :param dst: base image 
    :param src: superposition image
    :param alpha: superposition image opacity 
    """
    # alpha should be between 0 and 1 (alpha < 0 makes a rare inversion and alpha > 1 =overexposure)
    a = float(np.clip(alpha, 0.0, 1.0))
    # we sum the light of the hologram to the background 
    return cv2.addWeighted(dst, 1.0-a, src, a, 0)

def flicker(base_alpha, t, jitter=0.10):
    """
    This function introduces a small time-dependent variation in the hologram transparency to simulate flickering and instability typical of projected holograms.
    
    :param base_alpha: average transparency of the hologram 
    :param t: index time 
    :param jitter: controls how much does the variance can change
    """
    r = ((t*1103515245 + 12345) & 0x7fffffff) / 0x7fffffff
    j = (r - 0.5)*2.0*jitter
    return float(np.clip(base_alpha*(1.0 + j), 0.0, 1.0))
