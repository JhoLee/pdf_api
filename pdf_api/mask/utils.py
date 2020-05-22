import cv2
import numpy as np

"""
'none', 'skin', 'nose', 'eye_g', 'l_eye', 'r_eye', 
'l_brow', 'r_brow', 'l_ear', 'r_ear', 'mouth', 
'u_lip', 'l_lip', 'hair', 'hat', 'ear_r', 'neck_l', 
'neck', 'cloth'
"""


def gaussian_blur(img, mask):
    mask = np.stack((mask,)*3, axis=-1)
    blur_img = cv2.GaussianBlur(img, (127, 127), 0)
    out_img = np.where(mask, blur_img, img).astype(np.uint8)
    return out_img
