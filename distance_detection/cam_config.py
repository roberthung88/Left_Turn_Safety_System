import cv2
import numpy as np

# fc_left_x  0          cc_left_x
# 0          fc_left_y  cc_left_y
# 0          0          1
camera_matrix_left = np.array([[1180.69228, 0, 686.62824],[0, 1179.35396, 364.29618],[0, 0, 1]])
# kc_left = []
distortion_left = np.array([-0.07133, 0.35208, -0.00361, 0.00161, 0.00000])

# fc_right_x  0           cc_right_x
# 0           fc_right_y  cc_right_y
# 0           0           1
camera_matrix_right = np.array([[1177.97984, 0, 620.28398],[0, 1178.07470, 367.46573],[0, 0, 1]])
# kc_right = []
distortion_right = np.array([-0.03266, 0.19946, -0.00513, 0.00322, 0.00000])

# rotation vector
om = np.array([-0.01368, -0.00906, -0.00762])
R = cv2.Rodrigues(om)[0]
# translation vector
T = np.array([-60.71217, -0.69470, 0.39238])
# window size
size = (1280, 720)
R1,R2,P1,P2,Q,validPirxROI1, validPixROI2 = cv2.stereoRectify(camera_matrix_left, distortion_left, 
                                                              camera_matrix_right, distortion_right, size, R, T)

left_map1, left_map2 = cv2.initUndistortRectifyMap(camera_matrix_left, distortion_left, R1, P1, size, cv2.CV_16SC2)
right_map1, right_map2 = cv2.initUndistortRectifyMap(camera_matrix_right, distortion_right, R2, P2, size, cv2.CV_16SC2)