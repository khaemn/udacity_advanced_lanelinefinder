# Calibration and undistortion according to
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html

import glob
import cv2
import numpy as np
from os import path

CALIBRATION_IMG_PATH = 'camera_cal'

class CameraCalibrator:
    def __init__(self, nx=9, ny=6, img_type='*.jpg'):
        self.nx = nx
        self.ny = ny
        self.img_type = img_type
        self.objpoints = []
        self.img_shape = None
        self.mtx = None
        self.dist = None
        # prepare object points template, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((nx*ny, 3), np.float32)
        objp[:,:2] = np.mgrid[0:nx, 0:ny].T.reshape(-1,2)
        self.objp_template = objp
        self.imgpoints = []
        
    def crunch_image(self, img_filename):
        print("Crunching {} ...".format(img_filename))
        img = cv2.imread(img_filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.img_shape == None:
            self.img_shape = gray.shape
        elif gray.shape != self.img_shape:
            print("  warning: calibration images are not of "\
                  "the same size! expected {}, found {}"
                    .format(str(self.img_shape), str(gray.shape)))
        ret, corners = cv2.findChessboardCorners(gray, (self.nx, self.ny), None)
        if not ret:
            print("  warning: can not find chessboard corners on {}".format(img_filename))
            return
        self.objpoints.append(self.objp_template)
        self.imgpoints.append(corners)

    def calibrate(self, folder_path):
        search_pattern = path.join(folder_path, self.img_type)
        print('Searching for calibration images at ', search_pattern)
        filenames = glob.glob(path.join(folder_path, self.img_type))
        total_found = len(filenames)
        print("{} files found for calibration.".format(total_found))
        if total_found == 0:
            raise ValueError("Can not calibrate : no images.")
        
        for filename in filenames:
            self.crunch_image(filename)
        
        if len(self.imgpoints) == 0:
            raise ValueError("Can not calibrate : nothing found on given images.")
            
        ret, self.mtx, self.dist, rvecs, tvecs = cv2.calibrateCamera(
                self.objpoints, self.imgpoints, self.img_shape[::-1],None,None)
        if not ret:
            print("Error! Calibration failed!")
            return
        print("Calibration successful")

    def get_calibration_data(self):
        return self.mtx, self.dist
    
    def get_shape(self):
        return self.img_shape
    

class Undistorter():
    def __init__(self, mtx, dist, shape):
        self.mtx = mtx
        self.dist = dist
        self.own_shape = shape
        self.newcameramtx = None
        self.last_shape = None
        
    def crop(self, img):
        x,y,w,h = self.roi
        return img[y:y+h, x:x+w]
        
    def undistort(self, img):
        """ Expects a grayscale image as input """
        img_shape = img.shape
        assert(len(img_shape) == 2)
        # Re-initing output ROI and transform matrix each time we
        # get an image with a different shape.
        if self.last_shape != img_shape:
            self.last_shape = img_shape
            w, h = self.last_shape[::-1]
            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
                self.mtx, self.dist, (w,h), 1, (w,h))
        undistorted = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
        cropped = self.crop(undistorted)
        return cropped

