import cv2
from jetcam.csi_camera import CSICamera

file_path = "/home/nano/Desktop/output/"
#480x320
camera_right = CSICamera(capture_device=0, width=1280, height=720)
camera_left = CSICamera(capture_device=1, width=1280, height=720)
counter = 1

while True:
    image_right = camera_right.read()
    image_left = camera_left.read()
    cv2.imshow("right",image_right)
    cv2.imshow("left",image_left)

    if cv2.waitKey(1) & 0xFF == ord('s'): # press s to save image
        print("save capture{}".format(counter))
        cv2.imwrite(file_path+"right{}.jpg".format(counter),image_right)
        cv2.imwrite(file_path+"left{}.jpg".format(counter),image_left)
        counter=counter+1
    
    elif cv2.waitKey(1) & 0xFF == ord('q'): # press q to stop, or directly ctrl + C (lol)
        break
    
    else:
        #print("|")
        continue
cv2.destroyAllWindows()