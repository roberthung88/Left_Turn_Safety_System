import cv2
import numpy as np

# fc_left_x  0          cc_left_x
# 0          fc_left_y  cc_left_y
# 0          0          1
camera_matrix_left = np.array([[1250.12541, 0, 691.61850],[0, 1230.17838, 427.35528],[0, 0, 1]])
# kc_left = []
distortion_left = np.array([-0.05265, 0.14178, -0.00724, 0.00415, 0.00000])

# fc_right_x  0           cc_right_x
# 0           fc_right_y  cc_right_y
# 0           0           1
camera_matrix_right = np.array([[1193.23239, 0, 638.79370],[0, 1179.38126, 411.16069],[0, 0, 1]])
# kc_right = []
distortion_right = np.array([-0.18814, 0.66653, -0.00790, -0.00679, 0.00000])

# rotation vector
om = np.array([-0.01199, -0.00651, -0.00405])
R = cv2.Rodrigues(om)[0]
# translation vector
T = np.array([-47.47028, 6.13393, -20.83518])
# window size
size = (1280, 720)
R1,R2,P1,P2,Q,validPirxROI1, validPixROI2 = cv2.stereoRectify(camera_matrix_left, distortion_left, 
                                                              camera_matrix_right, distortion_right, size, R, T)

left_map1, left_map2 = cv2.initUndistortRectifyMap(camera_matrix_left, distortion_left, R1, P1, size, cv2.CV_16SC2)
right_map1, right_map2 = cv2.initUndistortRectifyMap(camera_matrix_right, distortion_right, R2, P2, size, cv2.CV_16SC2)
