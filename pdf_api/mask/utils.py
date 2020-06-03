import cv2
import numpy as np

"""
'none', 'skin', 'nose', 'eye_g', 'l_eye', 'r_eye', 
'l_brow', 'r_brow', 'l_ear', 'r_ear', 'mouth', 
'u_lip', 'l_lip', 'hair', 'hat', 'ear_r', 'neck_l', 
'neck', 'cloth'
"""


def gaussian_blur(img, mask, rate=127):
    """
    이미지에서 마스크 부분에 대해 흐림 효과 처리
    :param img: image
    :param mask: mask
    :type img: np.ndarray
    :type mask: np.ndarray
    :return: masked image with blurring
    """
    h, w, _ = img.shape
    w_rate, h_rate = w // 100 * rate, h // 100 * rate
    w_rate = w_rate + 1 if w_rate % 2 == 0 else w_rate
    h_rate = h_rate + 1 if h_rate % 2 == 0 else h_rate
    blur_img = cv2.GaussianBlur(img, (w_rate, h_rate), 0)
    out_img = np.where(mask, blur_img, img).astype(np.uint8)
    return out_img


def mosaic(img, mask, rate=10):
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
    h, w, _ = img.shape
    w_rate = w // 100 * rate
    h_rate = h // 100 * rate
    mosaic_img = cv2.resize(img, (w_rate, h_rate))
    mosaic_img = cv2.resize(mosaic_img, (w, h), interpolation=cv2.INTER_AREA)
    out_img = np.where(mask, mosaic_img, img).astype(np.uint8)
    return out_img


def combined_masking(img, mask, rate=(5, 15)):
    out_img = mosaic(img, mask, rate[0])
    out_img = gaussian_blur(out_img, mask, rate[1])
    return out_img
