## Writeup

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./examples/undistort_output.png "Undistorted"
[image2]: ./test_images/test1.jpg "Road Transformed"
[image3]: ./examples/binary_combo_example.jpg "Binary Example"
[image4]: ./examples/warped_straight_lines.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"

[illustration000]: ./writeup_images/0000_distorted.jpg                                 
[illustration001]: ./writeup_images/0001_undistorted.jpg                               
[illustration002]: ./writeup_images/0002_undistorted_plus_distorted.jpg                
[illustration003]: ./writeup_images/0003_distorted.jpg                                 
[illustration004]: ./writeup_images/0004_undistorted.jpg                               
[illustration005]: ./writeup_images/0005_undistorted_plus_distorted.jpg                
[illustration006]: ./writeup_images/0006_transform_roi.jpg                             
[illustration007]: ./writeup_images/0007_birds_eye.jpg                                 
[illustration008]: ./writeup_images/0008_transform_roi.jpg                             
[illustration009]: ./writeup_images/0009_birds_eye.jpg                                 
[illustration010]: ./writeup_images/0010_transform_roi.jpg                             
[illustration011]: ./writeup_images/0011_birds_eye.jpg                                 
[illustration012]: ./writeup_images/0012_hls_color_space.jpg                           
[illustration013]: ./writeup_images/0013_luminosity.jpg                                
[illustration014]: ./writeup_images/0014_saturation.jpg                                
[illustration015]: ./writeup_images/0015_yellow.jpg                                    
[illustration016]: ./writeup_images/0016_yellow_balanced.jpg                           
[illustration017]: ./writeup_images/0017_sat_plus_yellow.jpg                           
[illustration018]: ./writeup_images/0018_luminosity_balanced.jpg                       
[illustration019]: ./writeup_images/0019_luminosity_highcontrast.jpg                   
[illustration020]: ./writeup_images/0020_yellsat_balanced.jpg                          
[illustration021]: ./writeup_images/0021_yellsat_highcontrast.jpg                      
[illustration022]: ./writeup_images/0022_yellsat_mix_lum.jpg                           
[illustration023]: ./writeup_images/0023_yellsat_mix_lum_highcontrast.jpg              
[illustration024]: ./writeup_images/0024_yellsat_mix_lum_highcontrast_clamped.jpg      
[illustration025]: ./writeup_images/0025_abs_sobelx_kernel_3.jpg                       
[illustration026]: ./writeup_images/0026_abs_sobely_kernel_3.jpg                       
[illustration027]: ./writeup_images/0027_gradient_angles.jpg                           
[illustration028]: ./writeup_images/0028_gradient_magnitude.jpg
[illustration029]: ./writeup_images/0029_angle_magnitude_combined.jpg
[illustration030]: ./writeup_images/0030_found_lane_pixels.jpg
[illustration031]: ./writeup_images/0031_taken_lane_pixels.jpg
[illustration032]: ./writeup_images/0032_demo_lanes_detected.jpg                       
[illustration033]: ./writeup_images/0033_pipeline_result.jpg



## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

### Here I consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is encapsulated in `./camera_calibrator.py` two classes definition. The CameraCalibrator class should be parametrized with a calibration images folder on construction. Then, the method `calibrate()` iterates through the given folder and calls `crunch_image()` for each ".jpg" image found. All calibration images are expected to be of the same pixel size. After a successful calibration, the calibration data (camera matrix, distortion coefficients) can be retrieved via `get_calibration_data()`. As there is only one type of usage of the calibration information, I do not store other calibration data, such as rotation and  translation vectors.

The calibration process is implemented according to [this tutorial](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html).
I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp_template` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function, and store the calibration data in `mtx` and `dist` class fields respectively.

To undistort an image using the calibration data, I have created a separate class `Undistorter`.
The class should be parametrized with a calibration data and an expected image shape on construction.
Then, any image can be undistorted, using the `undistort()` method.

Original image               |  Undistorted image
:---------------------------:|:-------------------------:
![distorted][illustration000]|![undistorted][illustration001]

Below is a mix of an original and undistorted images, where the original one is in red, and the undistorted
in the blue channel of an image:

![undistorted and distorted together][illustration002]


### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

I have saved a grayscale distorted and undistorted road images, because that allows mixing them later using separate color channels to display the result. On a real road image, the difference between distorted and undistorted ones is not easily visible without channel mixing:

Grayscale img from camera    | Undistorted grayscale road image
:---------------------------:|:-------------------------:
![distorted][illustration003]|![undistorted][illustration004]

The resulting mix (original on red, undistorted on blue channel:

![undistorted and distorted together][illustration005]

As it can be easlily seen on the mixed road image, the camera distortions almost are not affecting the region where the lane lines are situated, so for this particular camera even a "raw", distorted image, would be good enough to find lanes and compute their curvature. However, as for a general approach, the undistortion is necessary by default.

#### 2. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

I have performed tons of experiments tryng to find the best approach to reliably detect lane pixels, and then I tried to do the perspective transform **first**, before the contrast improvement and other thresholdings. This actually helped me a lot to deal with the "challenging" video.

To perform the perspective transforms (to the "bird-eye" view and back from it to the "road" view) I have  implemented a separate class `Bird` (that has its eye, kek) in `bird.py`. It has two useful methods:

1. `.from_above(...)` that takes an image from camera and warps it to a bird-eye view
2. `.to_road(...)` that takse a bird-eye view and transforms it back to a camera view

While working on videos, it turned out that the "regular" and "challenge" videos have a bit different ROIs - probably, because of different camera position. So I have declared a `REGULAR_CAMERA_ROI` and a `CHALLENGE_CAMERA_ROI` arrays to use them separately.

```python
h_center = 640
h_offset = 50
top = 450
bottom = 690
left = 210
right = 1070
REGULAR_CAMERA_ROI = np.array([[left, bottom],
                               [h_center - h_offset, top],
                               [h_center + h_offset, top],
                               [right, bottom]]
                               , np.int32)
```
Please note the ROI points must be of a `np.int32` type to plot them on an image, but for the perspective  transform they must be of a `np.float32` type.

An instance of Bird should be parametrized with the two regions of interest: the first one represents 4 points on a 'bird-eye' view, and the second one represents a corresponding 4 points on a camera image.

For a regular video transformation, the ROIs are (starting from the bottom left point):

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 210, 690      | 260,  0       | 
| 590, 450      | 260,  720     |
| 690, 450      | 1020, 720     |
| 1070, 690     | 1020, 0       |


I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image:

Camera image ("road")        | Warped image ("from_above")
:---------------------------:|:-------------------------:
![road_view][illustration006]|![from_above][illustration007]
![road_view][illustration008]|![from_above][illustration009]
![road_view][illustration010]|![from_above][illustration011]

#### 3. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

I have tried many variations of thresholding an RGB or HLS image, but without additional efforts it is almost impossible to tell the lane line apart from the background on the "challenging" frames with low contrast or pavement color change.

So I have developed a contrast processing pipeline, that uses:

* "Yellow" channel (Red + Green - Blue)
* Saturation and luminosity channels
* Contrast improvement
    
    (All above is performed with `adaptive_vertical_contrast()` function)


* Vertical and close to vertical lines' pixels amplification and thresholding
    
    
    (Performed with `amplify_vert_lane_pixels()` function)

Also, most of the processing is being done on "downsampled" images. I have adjusted the downsampling (e.g. shrinking) rate to a values (about 4..8 depending on the stage) that increases processing speed without significant accuracy lost.

Road view                    | Warped image ("from_above")
:---------------------------:|:-------------------------:
![road_view][illustration008]|![from_above][illustration009]


Image in HLS (displayed in BGR) | "Yellow" channel (R + G - B) (downsampled)
:------------------------------:|:-------------------------:
![road_view][illustration012]   |![from_above][illustration015]

Saturation channel (ch 2 from HLS) | Luminosity channel (ch 1 from HLS)
:------------------------------:|:-------------------------:
![road_view][illustration014]   |![from_above][illustration013]

On some road images the contrast in saturation and yellow channels is poor, and the lane marking is not bright enough (as opposed to the pavement); but anyway while we have a pavement, the lane marking would always be brighter, and, probably it would be among the brightest objects in the image.
So I use this approach to improve contrast:

1. Find the most common pixel brightness (major tone) - presuming the lane marking is brighter
```python
# take histogram
hist = np.histogram(img)
# find the histogram peak == the most common brightness
major_tone = hist[1][np.argmax(hist[0])]
```
Note: the histogram is actually being taken from each N'th pixel, where N > 1, to increase the processing speed.

2. Subtract this value from all pixels - this way the most part of pavement becomes black
The result of major tone subtraction (I call it "balanced") is below:

Yellow              | Yellow balanced 
:------------------:|:------------------:
![][illustration015]|![][illustration016]

3. After balancing the image, the lane markings (highly probable) are the brightest parts of the image, so if we square all brightnesses, the distance between dim and bright part would significantly increase. Then the result of squaring is thresholded and normalized back to range 0..255.

```python
# Assume 'luminosity' is a 0..255 np.uint8 array, containing the luminosity channel
luminosity_highcontrast = np.minimum(np.power(luminosity.astype(np.uint16), 2), 2500))

```
After normalization back to 0..255 range, the brighter parts become much brighter, while the darker ones become black. I call this result a "highcontrast", here are all the "luminosity" channel processing stages for comparison:

Luminosity as-is    | Luminosity balanced| Luminosity highcontrast
:------------------:|:------------------:|:----------------------:
![][illustration013]|![][illustration018]|![][illustration019]

Meanwhile, the balanced yellow and the 'raw' saturation channel are summed. I have chosen this approach because the yellow lane marking might have a good brightness in both yellow channel and saturation channel, or in only one of them; but it is always much dimmer in luminosity channel (and of course is almost invisible in the blue channel).

Balanced yellow     | Saturation as-is   | 50% yellow + 50% saturation
:------------------:|:------------------:|:----------------------:
![][illustration016]|![][illustration014]|![][illustration017]

The Yellow+Saturation sum then is being made high-contrast, as described above:

 50% yellow + 50% saturation | yell + sat balanced | yell + sat highcontrast
:---------------------------:|:-------------------:|:----------------------:
![][illustration017]         |![][illustration020] |![][illustration021]  

After that we have the best possible contrast for a yellow lane marking in the `yell_sat_highcontrast`, and the best possible contrast for a white lane marking in `luminosity_highcontrast`, so I take the max value from both images to make an image where both lane markings are very bright, and the rest is dark:

 yell + sat highcontrast| Luminosity highcontrast | Maximum of both
:----------------------:|:-----------------------:|:-----------------:
![][illustration021]    |![][illustration019]     |![][illustration022]

This image is again processed to highcontrast to increase signa/noise ratio for furter processing:

![Highcontrast lane markings][illustration024]

Now it is time to use the geometrical information to separathe just a bright object from a lane marking. Assuming we have already warped the image, the lane markings would be always close to vertical, with a small angle difference from 90 degrees. Also, the lane markings (especially after several rounds of highcontrasting) would have a very sharp edges, e.g. the brightness gradient on them would have a high absolute magnitude.

To compute and threshold the angles, first take Sobel 'x' and 'y' component filters:

 Sobel filter, `x`  | Sobel filter, `y`
:------------------:|:------------------:
![][illustration025]|![][illustration026]

Then compute the angle and the gradient magnitude:

 Probable angle     | `x+y` gradient magnitude
:------------------:|:------------------:
![][illustration027]|![][illustration028]

Then we take only a pixels, that are both in some angle range *and* have a gradient magnitude above a threshold. That is the final result of the preprocessing pipeline:

![][illustration029]


#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

The pipeline uses 2 approaches for detecting lane pixels: a slower one, that is based on a sliding window and histogramming; and a faster one, which only takes all white pixels in the vicinity of a polynome curve. Of course, the second method is only applicable when the lane is already detected.

The sliding window method is implemented in the `find_lane_pixels()` function. It uses 9 steps per 720 pixels of an image height and the window total width is 200 pixels.

The input image (white), found lane curves (yellow and cyan), their respective pixels and the searching windows (green) are plotted below:

![found_lane_pixels][illustration030]

The second method just makes N windows along the known lane curves. The curves are being passed as a parameter to the `take_lane_pixels()` function. Then any non-zero pixel from the search (e.g. covered by rectangular windows) area is taken as new lane pixels. The lane curves, (yellow and cyan), their respective pixels and the searching area (grey) are plotted below:

![taken_lane_pixels][illustration031]

Based on the lane pixels, 2 curve polynomes are being fit in the `fit_polynomial()` function. In the images above the thin yellow and cyan line already represents the curves. Validation of the found lane curves might be done via plotting them (with a corresponding "unwarping" transform, made by `Bird.to_road()` method) to the road image:

![demo_lanes_detected][illustration032]


#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

To track the lane lines, I have implemented a `LaneLine` class in `lane_line.py`.
When contructing, this class must be parametrized with a horizontal pixels-per-meter ratio `xm_per_pix` and a vertical one (`ym_per_pix`), as they depend on a particular ROI of the "bird", e.g. on the warp trasnformation parameters. Also there is an important `avg_depth` construction parameter, that sets the averaging coefficient in the simple averaging functions:

``` python3
# Presume we have some value, named `old_value` and equal to, say, 10
# and a new_value, equal to 50
avg_depth = 64
averaged = (old_value * (avg_depth - 1) + new_value) / avg_depth
# Now the 'averaged' is 10,625 - e.g. the glitch is filtered.
# After this, we need to save the existing data as an old one for next iteration.
old_value = averaged
```
I use this averaging approach in all cases whenever the averaging is required in this project. The formula above has a useful properties: 
1. If the values we work with are integers, all the math can be done in integer domain (which is fast)
2. If the averaging coefficient is a power of 2, the division and multiplication can be replaced with a combinantion of only biary shifts and addition/subtraction, which is much faster.
In the scope of this particular project I did not reimplement the averager as described above, however in a C++ production code for such a task I would definitely use this approach (and I have tested it a lot during my career, it is especially cool in embedded devices with slow FP math).

The class holds the the approximation polynome (`.avg_fit`), the curvature radius at the bottom (e.g. at the closest point to the car) (`.radius_m`), and the offset of a virtual lane center from the real screen center (and center of the car, by definition) (`.line_base_pos_mm`). For retrieving these values there are `get_fit()`, `get_radius()` and `get_horizontal_offset()` getters respectively.

There must be 2 instances of the class, for the left and right lane.

The `LaneLine` class computes all the necessary points when the `update()` method is called, this method takes an array of 3 polynomial coefficients. To prevent corrupting the data when a broken frame frame arrives, there are two mechanisms:
1. An absolute difference between the old and new coefficients is calculated. If this diff is above some predefined threshold, the new data is ignored, and the broken frame counter is incremented; the threshold is an experimentally adjusted value and might differ from video to video.
2. If the diff is below the allowed threshold, the lane polynome (`.avg_fit`) is being updated, using averaging with the existing data, to smooth any glitches.


#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

The resulting pipeline is contained in the `process_frame()` function. It takes an image from camera, performs contrast preprocessing and geometry search and stores a high-contrast bird-eye image of the (possible) lane into an averaging buffer. This buffer helps to preserve the most valuable information about the pixels, that move vertically from frame to frame and filter out small pixel noise. Then, basing on this high-contrast image, the pipeline fits 2 curves to represent left and right lane borders. After finding bordes, the pipeline plots the lane shape (polygon) back to the initial image, and also plots information about lane curvature radius and car offset.


![pipeline_result][illustration033]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to regular video result](./test_video_output/submit_test_video.mp4)
(Alternative link on YouTube https://youtu.be/_g7uUsdl48s)

Conclusion: on the regular video the pipeline works fine.

Here's a [link to challenge video result](./test_video_output/submit_challenge_test_video.mp4)
(Alternative link on YouTube https://youtu.be/5d3rigBNc3k)

Conclusion: even on the "challenge" video there is no totall loss of lane markings recognition. The lane curvature radius somtimes is detected incorrectly _high_, but I would say that is not a problem, as the big curvature radius means a straight lane; and a misunderstood straight lane (when in reality it is a curve with some big radius) would not be a problem for a car, if the radius is measured correctly in the next several frames.

*Note:* I did not manage to found any working solution for the "harder challenge". I am pretty sure that the search window pixel finding would not work on that video (due to small curvature radius of the lane) and requires a significant change of the lane pixel finding algorithm. I believe it is still possible, but requires a shitload of time for developing and testing such algorithm, which is by far out of scope of this project.

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

The most significant issue of the pipeline is the hardcoded thresholds and ROIs, that are now adjusted to 2 particular videos. In case of another road pavement colours and/or lighting (such as morning/evening sun) I presume it would not work without re-adjusting all these hardcoded numbers, and that's a ton of work.

Also, the contrast processing part (`adaptive_vertical_contrast()`) might be an overkill for the "regular" video, but I decided to have one pipeline for both regular and challenge ones. The contrast processing function might be simpler (and faster), but I have no idea how to improve it, except try-and-fail approach. Unfortunately, I have not found any description or hints in the lectures about how to implement a corresponding processing for "challenge" and "harder challenge" videos. After I submit this project, I am going to search for the solution among existing repostiories - I believe there _should_ be a solution somewhere ;)

Overall, the code in the notebook is not a production one, with next issues:
1. Global variables and objects usage.
2. The "left" and "right" lane objects would be better managed by another object to compose a pipeline.
3. The `ImagePrinter` class usage is ugly, but it was the most convenient way to store all the pictures I need from the various pipeline stages. I would remove it from any practical solution for sure. 
