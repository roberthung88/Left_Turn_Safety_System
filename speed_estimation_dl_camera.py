# USAGE
# NOTE: When using an input video file, speeds will be inaccurate
# because OpenCV can't throttle FPS according to the framerate of the
# video. This script is for development purposes only.
#
# python3 speed_estimation_dl_video.py --conf config/config.json --input sample_data/ezgif.com-gif-maker.mp4

# inform the user about framerates and speeds
print("[INFO] NOTE: When using an input video file, speeds will be " \
	"inaccurate because OpenCV can't throttle FPS according to the " \
	"framerate of the video. This script is for development purposes " \
	"only.")

# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.utils import Conf
from imutils.video import VideoStream
from imutils.io import TempFile
from imutils.video import FPS
from datetime import datetime
from threading import Thread
import numpy as np
import argparse
import imutils
import dlib
import time
import cv2
import os
import matplotlib.pyplot as plt
import data_collection as ds
import padasip as pa 

import cam_config
from jetcam.csi_camera import CSICamera
import math

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="Path to the input configuration file")
ap.add_argument("-i", "--input", required=True,
	help="Path to the input video file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# initialize the list of class labels MobileNet SSD was trained to
# detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(conf["prototxt_path"],
	conf["model_path"])
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)


# camera initialize, set resolution as 1280x720
print("[INFO] warming up camera...")
camera_right = CSICamera(capture_device=0, width=1280, height=720)
camera_left = CSICamera(capture_device=1, width=1280, height=720)
time.sleep(2.0)

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
H = None
W = None
cnt = 0


# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers, followed by a dictionary to
# map each unique object ID to a TrackableObject
ct = CentroidTracker(maxDisappeared=conf["max_disappear"],
	maxDistance=conf["max_distance"])
trackers = []
trackableObjects = {}

# keep the count of total number of frames
totalFrames = 0

# initialize the log file
logFile = None

# initialize the list of various points used to calculate the avg of
# the vehicle speed
# points = [("A", "B"), ("B", "C"), ("C", "D")]

# start the frames per second throughput estimator
fps = FPS().start()

# loop over the frames of the stream
while True:
    # read the frames from the camera
    frame_right = camera_right.read()
    frame_left = camera_left.read()
    
    # rectify the frames
    # use left_rectify as detection frame input
    frame_right_rectify = cv2.remap(frame_right, cam_config.right_map1, cam_config.right_map2, cv2.INTER_LINEAR)
    frame_left_rectify = cv2.remap(frame_left, cam_config.left_map1, cam_config.left_map2, cv2.INTER_LINEAR)
    
    # create gray-scale frames for depth graph
    frame_right_gs = cv2.cvtColor(frame_right_rectify, cv2.COLOR_BGR2GRAY)
    frame_left_gs = cv2.cvtColor(frame_left_rectify, cv2.COLOR_BGR2GRAY)
    
    # create depth graph "disp"
    # create 3D coordinate model "threeD"
    num = 10 #num & blockSize can be modified for better outcome
    blockSize = 31
    
    stereo = cv2.StereoBM_create(numDisparities = 16*num, blockSize = 31)
    disparity = stereo.compute(frame_left_gs,frame_right_gs)
    disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    threeD = cv2.reprojectImageTo3D(disparity.astype(np.float32)/16., cam_config.Q)
    
    # store the current timestamp, and store the new date
	ts = datetime.now()
	newDate = ts.strftime("%m-%d-%y")

	# check if the frame is None, if so, break out of the loop
	if frame_right & frame_left is None:
		break

	# if the log file has not been created or opened
	if logFile is None:
		# build the log file path and create/open the log file
		logPath = os.path.join(conf["output_path"], conf["csv_name"])
		logFile = open(logPath, mode="a")

		# set the file pointer to end of the file
		pos = logFile.seek(0, os.SEEK_END)
		logFile.write("Year,Month,Day,Time (in MPH),Speed\n")

    # I cancel the resize here, is it a must to resize the frame?
    # if it is, change the resolution when intializing the camera
    # also remember to change the size in camera_config.py
	rgb = cv2.cvtColor(frame_left_rectify, cv2.COLOR_BGR2RGB)

	# if the frame dimensions are empty, set them
	# if W is None or H is None:
	# 	meterPerPixel = conf["distance"] / W
	# 	(H, W) = frame.shape[:2]

	# initialize our list of bounding box rectangles returned by
	# either (1) our object detector or (2) the correlation trackers
	rects = []
    
    # initialize distance container
    distance_list = []
    
	# check to see if we should run a more computationally expensive
	# object detection method to aid our tracker
	if totalFrames % conf["track_object"] == 0:
		# initialize our new set of object trackers
		trackers = []

		# convert the frame to a blob and pass the blob through the
		# network and obtain the detections
		blob = cv2.dnn.blobFromImage(frame_left_rectify, size=(1280, 720),
			ddepth=cv2.CV_8U)
		net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5,
			127.5, 127.5])
		detections = net.forward()

		# loop over the detections
		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated
			# with the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence`
			# is greater than the minimum confidence
			if confidence > conf["confidence"]:
				# extract the index of the class label from the
				# detections list
				idx = int(detections[0, 0, i, 1])

				# if the class label is not a car, ignore it
				if CLASSES[idx] != "car":
					continue

				# compute the (x, y)-coordinates of the bounding box
				# for the object
				box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
				global startX, startY, endX, endY
				(startX, startY, endX, endY) = box.astype("int")
				#data_collection(startX, startY, endX, endY, timestamp)

				# draws rectangle
				cv2.rectangle(frame_left_rectify, (startX, startY), (endX, endY),(0, 255, 0), 2)

				
				# print("StartX & EndX", startX, endX)
				# print("StartY & EndY", startY, endY)


				# print("EndY", endY)
				
				# gets snapshot of vehicles
				#plt.imshow(frame[startY:endY,startX:endX], interpolation='nearest')
				#plt.show()
				

				# construct a dlib rectangle object from the bounding
				# box coordinates and then start the dlib correlation
				# tracker
				tracker = dlib.correlation_tracker()
				rect = dlib.rectangle(startX, startY, endX, endY)
				tracker.start_track(rgb, rect)

				# add the tracker to our list of trackers so we can
				# utilize it during skip frames
				trackers.append(tracker)

	# otherwise, we should utilize our object *trackers* rather than
	# object *detectors* to obtain a higher frame processing
	# throughput
	else:
		# loop over the trackers
		for tracker in trackers:
			# update the tracker and grab the updated position
			tracker.update(rgb)
			pos = tracker.get_position()

			# unpack the position object
			startX = int(pos.left())
			startY = int(pos.top())
			endX = int(pos.right())
			endY = int(pos.bottom())


			cv2.rectangle(frame_left_rectify, (startX, startY), (endX, endY),(0, 255, 0), 2)
			# add the bounding box coordinates to the rectangles list
			rects.append((startX, startY, endX, endY))
            center_X = (startX + endX)/2
            center_Y = (startX + endY)/2
            # add the distances to distance list
            # threeD[y][x][0/1/2] means x,y,z coordinate
            # distance in mm, /1000 to convert to m
            distance_list.append(sqrt(pow(threeD[center_Y][center_X][0],2) 
                                    + pow(threeD[center_Y][center_X][1],2)
                                    + pow(threeD[center_Y][center_X][2],2))/1000)
            
	# use the centroid tracker to associate the (1) old object
	# centroids with (2) the newly computed object centroids
	objects = ct.update(rects)


	
	# loop over the tracked objects
	for (objectID, centroid) in objects.items():
		# check to see if a trackable object exists for the current
		# object ID
		to = trackableObjects.get(objectID, None)

		filt = pa.filters.FilterLMS(1, mu=2)

		# if there is no existing trackable object, create one
		if to is None:
			to = TrackableObject(objectID, centroid)
		
		# Note: centroid[i] = (cX, cY)
		
		to.distance = ds.distance_detection(to, centroid[1])
		y = filt.predict(centroid[1])
		filt.adapt(to.distance, centroid[1])

		if to.lastLoc == 0:
			# no last location recorded, so add and not calculate speed
			to.lastLoc = centroid[1]
		else:
			to.speedMPH = ds.data_collection(to.lastLoc, centroid[1])
			if to.speedMPH > 0: 
				if cnt == 0:
					# if objectID == 1 or objectID == 3:
					
					print("[INFO] Speed of the vehicle that just passed"\
					" is: {:.2f} MPH".format(to.speedMPH))
					
					# print("[INFO] Distance of the vehicle {:.2f}"\
					# " is: {:.2f} feet".format(objectID, to.distance))

					# print("[INFO] Y-coord of the vehicle {:.2f}"\
					# " is: {:.2f}.".format(objectID, centroid[1]))
					cnt = 0
				else:
					cnt+=1
			else:
				None	

		# store the trackable object in our dictionary
		trackableObjects[objectID] = to

		# draw both the ID of the object and the centroid of the
		# object on the output frame
        
		text = "ID {}".format(objectID)
		cv2.putText(frame_left_rectify, text, (centroid[0] - 10, centroid[1] - 10)
			, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		cv2.circle(frame_left_rectify, (centroid[0], centroid[1]), 4,
			(0, 255, 0), -1)

		# check if the object has not been logged
		if not to.logged:
			# check if the object's speed has been estimated and it
			# is higher than the speed limit
			if to.estimated and to.speedMPH > conf["speed_limit"]:
				# set the current year, month, day, and time
				year = ts.strftime("%Y")
				month = ts.strftime("%m")
				day = ts.strftime("%d")
				time = ts.strftime("%H:%M:%S")

				# log the event in the log file
				info = "{},{},{},{},{}\n".format(year, month,
					day, time, to.speedMPH)
				logFile.write(info)

				# set the object has logged
				to.logged = True

	# if the *display* flag is set, then display the current frame
	# to the screen and record if a user presses a key
	if conf["display"]:
		cv2.imshow("frame_left_rectify", frame_left_rectify)
        cv2.imshow("depth",disp)
		key = cv2.waitKey(24) & 0xFF

		# if the `q` key is pressed, break from the loop
		if key == ord("q"):
			break

	# increment the total number of frames processed thus far and
	# then update the FPS counter
	totalFrames += 1
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# check if the log file object exists, if it does, then close it
if logFile is not None:
	logFile.close()

# close any open windows
cv2.destroyAllWindows()

# clean up
print("[INFO] cleaning up...")
vs.release()
