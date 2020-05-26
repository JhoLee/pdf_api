import cv2
import numpy as np

"""
'none', 'skin', 'nose', 'eye_g', 'l_eye', 'r_eye', 
'l_brow', 'r_brow', 'l_ear', 'r_ear', 'mouth', 
'u_lip', 'l_lip', 'hair', 'hat', 'ear_r', 'neck_l', 
'neck', 'cloth'
"""


def gaussian_blur(img, mask):
    """
    이미지에서 마스크 부분에 대해 흐림 효과 처리
    :param img: image
    :param mask: mask
    :type img: np.ndarray
    :type mask: np.ndarray
    :return: masked image with blurring
    """
    mask = np.stack((mask,) * 3, axis=-1)
    blur_img = cv2.GaussianBlur(img, (127, 127), 0)
    out_img = np.where(mask, blur_img, img).astype(np.uint8)
    return out_img


def mosaic(img, mask, rate=25):
    """
    이미지에서 마스크 부분에 대해 모자이크 처리
    :param img: image
    :param mask: mask
    :param rate: mosaic rate
    :type img: np.ndarray
    :type mask: np.ndarray
    :type rate: int
    :return: masked image with mosaic
    """
    mask = np.stack((mask,) * 3, axis=-1)
    h, w, _ = img.shape
    mosaic_img = cv2.resize(img, (w // rate, h // rate))
    mosaic_img = cv2.resize(mosaic_img, (w, h), interpolation=cv2.INTER_AREA)
    out_img = np.where(mask, mosaic_img, img).astype(np.uint8)
    return out_img
