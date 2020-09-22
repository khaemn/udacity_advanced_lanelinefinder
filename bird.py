import cv2
import numpy as np

class Bird():
    def __init__(self, roi, camera_roi):
        # ROIs are expected to be np.float32 arrays of shape (4, 2)
        # describing a region starting from the bottom left point clockwise
        self.roi = roi
        self.camera_roi = camera_roi
        self.M = cv2.getPerspectiveTransform(camera_roi, roi)
        self.invM = cv2.getPerspectiveTransform(roi, camera_roi)
    
    def from_above(self, img):
        return cv2.warpPerspective(img, self.M, 
                                   (img.shape[1], img.shape[0]),
                                   flags=cv2.INTER_LINEAR)
    
    def to_road(self, img):
        return cv2.warpPerspective(img, self.invM, 
                                   (img.shape[1], img.shape[0]),
                                   flags=cv2.INTER_LINEAR)
    @staticmethod
    def plot_roi_on(img, roi):
        if len(img.shape) == 2:
            output = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            output = img.copy()
        roi_color = (255, 0, 255)
        thickness = 4
        cv2.polylines(output, [roi], True, roi_color, thickness)
        return output
