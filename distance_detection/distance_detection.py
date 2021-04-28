import cv2
import numpy as np
import cam_config
from jetcam.csi_camera import CSICamera

camera_right = CSICamera(capture_device=0, width=1280, height=720)
camera_left = CSICamera(capture_device=1, width=1280, height=720)

cv2.namedWindow("depth")
def callbackFunc(e, x, y, f, p):
    if e == cv2.EVENT_LBUTTONDOWN:
        print (threeD[y][x][2])

cv2.setMouseCallback("depth", callbackFunc, None)

cv2.createTrackbar("num","depth",2,10, lambda x: None)
cv2.createTrackbar("blockSize","depth",5,255,lambda x:None)

while True:
    image_right = camera_right.read()
    image_left = camera_left.read()
    # cv2.imshow("right",image_right)
    # cv2.imshow("left",image_left)
    image_right_rectify = cv2.remap(image_right, cam_config.right_map1, cam_config.right_map2, cv2.INTER_LINEAR)
    image_left_rectify = cv2.remap(image_left, cam_config.left_map1, cam_config.left_map2, cv2.INTER_LINEAR)
    # cv2.imshow("right_rectify",image_right_rectify)
    # cv2.imshow("left_rectify",image_left_rectify)

    image_right_gs = cv2.cvtColor(image_right_rectify, cv2.COLOR_BGR2GRAY)
    image_left_gs = cv2.cvtColor(image_left_rectify, cv2.COLOR_BGR2GRAY)

    num = cv2.getTrackbarPos("num", "depth")
    blockSize = cv2.getTrackbarPos("blockSize","depth")
    if blockSize % 2 == 0:
        blockSize += 1
    if blockSize < 5:
        blockSize = 5
    
    stereo = cv2.StereoBM_create(numDisparities = 16*num, blockSize = 31)
    disparity = stereo.compute(image_left_gs,image_right_gs)
    disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    threeD = cv2.reprojectImageTo3D(disparity.astype(np.float32)/16., cam_config.Q)

    cv2.imshow("left_rectify",image_left_rectify)
    cv2.imshow("depth",disp)
    if cv2.waitKey(24):
        continue
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break
        cv2.destroyAllWindows()

cv2.destroyAllWindows()