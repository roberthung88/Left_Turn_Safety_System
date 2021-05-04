import cv2
import numpy as np
import cam_config
from jetcam.csi_camera import CSICamera

#initialize camera
camera_right = CSICamera(capture_device=0, width=1280, height=720)
camera_left = CSICamera(capture_device=1, width=1280, height=720)

# set mouse callback, clicking one point (x,y) on "depth" window
# it will print out real-world 3D coordinate threeD[y][x][0/1/2] of the point (x,y)

# when combining with car_detection, use left_recify as video source
# after detecting a car, get the (x,y) of the car and input to threeD[y][x][ ] to get 3D coordinate
# you may ask why using "left_rectify" as car_detection video source, but threeD is from "depth"
# points on depth and left_rectify are the same in real world, they share the same x-y coordinate

cv2.namedWindow("depth")
def callbackFunc(e, x, y, f, p):
    if e == cv2.EVENT_LBUTTONDOWN:
        print (threeD[y][x][2])

cv2.setMouseCallback("depth", callbackFunc, None)

# two trackbars on "depth" window for you to change parameters while running code
# when a final pair of parameters is determined, these trackbars are not needed
cv2.createTrackbar("num","depth",2,10, lambda x: None)
cv2.createTrackbar("blockSize","depth",5,255,lambda x:None)

while True:
    # read the frame captured by the camera
    image_right = camera_right.read()
    image_left = camera_left.read()
    # cv2.imshow("right",image_right)
    # cv2.imshow("left",image_left)
    
    # rectify the image
    image_right_rectify = cv2.remap(image_right, cam_config.right_map1, cam_config.right_map2, cv2.INTER_LINEAR)
    image_left_rectify = cv2.remap(image_left, cam_config.left_map1, cam_config.left_map2, cv2.INTER_LINEAR)
    # cv2.imshow("right_rectify",image_right_rectify)
    # cv2.imshow("left_rectify",image_left_rectify)
    
    # convert the image to gray-scale (preparation for creating a depth grah)
    image_right_gs = cv2.cvtColor(image_right_rectify, cv2.COLOR_BGR2GRAY)
    image_left_gs = cv2.cvtColor(image_left_rectify, cv2.COLOR_BGR2GRAY)
    
    # getting the parameter "num" from trackbar
    num = cv2.getTrackbarPos("num", "depth")
    blockSize = cv2.getTrackbarPos("blockSize","depth")
    if blockSize % 2 == 0:
        blockSize += 1
    if blockSize < 5:
        blockSize = 5
    
    # create "threeD" the 3D model, don't need to understand the next four lines, but just know the "threeD" is what we need
    stereo = cv2.StereoBM_create(numDisparities = 16*num, blockSize = 31)
    disparity = stereo.compute(image_left_gs,image_right_gs) # combine the left and right grayscale images to create a depth graph
    disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    threeD = cv2.reprojectImageTo3D(disparity.astype(np.float32)/16., cam_config.Q)
    
    # display both left_rectify and "depth"
    cv2.imshow("left_rectify",image_left_rectify)
    cv2.imshow("depth",disp)
    
    # waitKey() is the time delay in ms between frame and frame, here I set 24ms between each frame
    if cv2.waitKey(24):
        continue
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break
        cv2.destroyAllWindows()

cv2.destroyAllWindows()
