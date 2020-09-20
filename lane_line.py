import numpy as np

'''
The LaneLine class implements functionality for tracking a lane line.
Usage:
1. Create an instance, setting the Y and X meter-per-pixel rates
2. Call update() each time a frame has been processed
3. To retrieve a curvature radius or a polynome, call corresponding getters.
'''

class LaneLine():
    def __init__(self, xm_per_pix, ym_per_pix, img_size=(1280, 720), avg_depth=8,
                 max_broken_frames=15, max_valid_diff=2.0, name="Unnamed"):
        self.avg_depth = avg_depth
        self.xm_per_pix = xm_per_pix
        self.ym_per_pix = ym_per_pix
        self.img_width, self.img_height = img_size
        self.max_broken_frames = max_broken_frames
        self.name = name
        self.max_valid_diff = max_valid_diff
        self.reset()
        
    def reset(self):
        # Poly coefficients. averaged during last N calls
        self.avg_fit = None
        self.isValid = False
        # Lane curvature radius in meters
        self.radius_m = 1e3
        # Distance in meters of vehicle center from the line
        # (assuming the car is centered and the lane width is 3.75 meters)
        self.line_base_pos_mm = 3750./2
        self.lane_h_center_mm = (self.img_width // 2) * self.xm_per_pix * 1000.
        self.broken_frames = 0
        self.curve = np.uint8([[0,0]])
        print("Inititalized Lane with center point at {}, full road {}, (half lane at {})"
              .format(self.lane_h_center_mm, self.img_width * self.xm_per_pix * 1000., self.line_base_pos_mm))

    def update(self, poly, x_pixels=None, y_pixels=None):
        if x_pixels is not None:
            self.x_pixels = x_pixels
        if y_pixels is not None:
            self.y_pixels = y_pixels
        if self.avg_fit is None:
            self.avg_fit = poly
        diff = np.absolute(self.avg_fit - poly)
        weighted_diff = np.absolute(diff[0]) + np.absolute(diff[1]) + np.absolute(diff[2])
        if weighted_diff > self.max_valid_diff:
            self.broken_frames += 1
            if self.broken_frames > self.max_broken_frames // 2:
                self.isValid = False
            if self.broken_frames > self.max_broken_frames:
                print("ALARM! LANE {} BROKEN!".format(self.name))
                self.avg_fit = (self.avg_fit * (self.avg_depth - 1) + poly) / self.avg_depth
        else:
            self.avg_fit = (self.avg_fit * (self.avg_depth - 1) + poly) / self.avg_depth
            self.isValid = True
            self.broken_frames = 0
        # Compute curvature
        new_curvature = self.curvature(self.avg_fit, self.img_height * self.ym_per_pix)
        self.radius_m = (self.radius_m * (self.avg_depth - 1) + new_curvature) / self.avg_depth
        # Compute lane center offset
        self.line_base_pos_mm = self.evaluate_poly2(
            self.avg_fit, self.img_height * self.ym_per_pix) * 1000 - self.lane_h_center_mm
            
    def set_curve(self, curve):
        """ Expects a numpy array of points (x,y)"""
        self.curve = curve
        
    def get_curve(self):
        return self.curve
        
    def get_fit(self):
        return self.avg_fit
    
    @staticmethod
    def evaluate_poly2(poly, y):
        # Evaluates a 2-grade polynomial
        return poly[0]*y*y + poly[1]*y + poly[2]
    
    @staticmethod
    def curvature(polynome, ycoord):
        if polynome is None:
            return 0.
        A, B, C = polynome
        numerator = np.power((1 + np.power((2 * A * ycoord + B), 2)), 3/2)
        denominator = 2 * np.abs(A)
        return numerator / denominator
    
    def get_radius(self):
        return self.radius_m
    
    def get_horizontal_offset(self):
        return self.line_base_pos_mm
        
    def is_valid(self):
        return self.isValid