import cv2
import numpy as np
import cam_config
from jetcam.csi_camera import CSICamera

camera_right = CSICamera(capture_device=0, width=1280, height=720)
camera_left = CSICamera(capture_device=1, width=1280, height=720)

#SGBM parameters
# mindisparity = 32
# ndisparities = 176
# SADWindowsSize = 16
# P1 = 4 * 1 * SADWindowsSize
# P2 = 32 * 1 * SADWindowsSize

# sgbm = cv2.StereoSGBM_create(mindisparity, ndisparities, SADWindowsSize)
# sgbm.setP1(P1)
# sgbm.setP2(P2)
# sgbm.setPreFilterCap(60)
# sgbm.setUniquenessRatio(30)
# sgbm.setSpeckleRange(2)
# sgbm.setSpeckleWindowSize(200)
# sgbm.setDisp12MaxDiff(1)
# disp sgbm.compute()

image_right = camera_right.read()
image_left = camera_left.read()
# cv2.imshow("right",image_right)
# cv2.imshow("left",image_left)

image_right_rectify = cv2.remap(image_right, cam_config.right_map1, cam_config.right_map2, cv2.INTER_LINEAR)
image_left_rectify = cv2.remap(image_left, cam_config.left_map1, cam_config.left_map2, cv2.INTER_LINEAR)
# cv2.imshow("right_rectify",image_right_rectify)
# cv2.imshow("left_rectify",image_left_rectify)

# image_right_gs = cv2.cvtColor(image_right, cv2.COLOR_BGR2GRAY)
# image_left_gs = cv2.cvtColor(image_left, cv2.COLOR_BGR2GRAY)

# image_right_gs_rectify = cv2.remap(image_right_gs, cam_config.right_map1, cam_config.right_map2, cv2.INTER_LINEAR)
# image_left_gs_rectify = cv2.remap(image_left_gs, cam_config.left_map1, cam_config.left_map2, cv2.INTER_LINEAR)

#disparity
# disp = sgbm.compute(image_left_gs_rectify, image_right_gs_rectify)

# xyz_coordinate = cv2.reprojectImageTo3D(disp, cam_config.Q, handleMissingValues = True)
# xyz_coordinate = xyz_coordinate*16

# disp = disp.astype(np.float32) / 16.0
# disp8U = cv2.normalize(disp, disp, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype = cv2.CV_8U)
# disp8U = cv2.medianBlur(disp8U, 9)

def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("point(%d, %d)" % (x, y))
        cv2.imwrite("/home/nano/Desktop/demo/right_x.jpg",image_right_rectify)

cv2.imshow("right_rectify", image_right_rectify)
cv2.setMouseCallback("right_rectify", onMouse, 0)

cv2.waitKey(0) # set time delay between each frame
   

cv2.destroyAllWindows()