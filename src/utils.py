"""
Utility functions for Satpam Laptop
"""
import cv2
import os
from datetime import datetime
from .config import CAPTURES_DIR

def get_capture_filename():
    """Generate unique filename for intruder capture"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(CAPTURES_DIR, f"intruder_{timestamp}.jpg")

def save_capture(frame, filename=None):
    """Save frame as image file"""
    if filename is None:
        filename = get_capture_filename()
    cv2.imwrite(filename, frame)
    return filename

def get_face_histogram(gray_frame, face_rect):
    """Ambil histogram dari area wajah untuk perbandingan"""
    x, y, w, h = face_rect
    face_roi = gray_frame[y:y+h, x:x+w]
    face_roi = cv2.resize(face_roi, (100, 100))
    hist = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist, face_roi

def compare_faces(hist1, hist2):
    """Bandingkan dua histogram wajah, return similarity score 0-1"""
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score
