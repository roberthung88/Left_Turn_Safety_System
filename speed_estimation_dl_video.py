# Usage: Run this command, with the last parameter changed to any video clip
# May need to install necessary packages
# python3 speed_estimation_dl_video.py --conf config/config.json --input sample_data/ezgif.com-gif-maker.mp4

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
import safety_system as ss
import padasip as pa 

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

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] warming up camera...")
#vs = VideoStream(src=0).start()
vs = cv2.VideoCapture(args["input"])
time.sleep(2.0)

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
H = None
W = None
num_zeros = 0
counter = 0 # flag to toggle print statements

# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers, followed by a dictionary to
# map each unique object ID to a TrackableObject
ct = CentroidTracker(maxDisappeared=conf["max_disappear"],
	maxDistance=conf["max_distance"])
trackers = []
trackableObjects = {}

# keep the count of total number of frames
totalFrames = 0

# start the frames per second throughput estimator
fps = FPS().start()

# loop over the frames of the stream
while True:
	# grab the next frame from the stream, store the current
	# timestamp, and store the new date
	ret, frame  = vs.read()
	ts = datetime.now()
	newDate = ts.strftime("%m-%d-%y")

	# check if the frame is None, if so, break out of the loop
	if frame is None:
		break

	# resize the frame
	frame = imutils.resize(frame, width=conf["frame_width"])
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# if the frame dimensions are empty, set them
	if W is None or H is None:
		(H, W) = frame.shape[:2]
		# meterPerPixel = conf["distance"] / W

	# initialize our list of bounding box rectangles returned by
	# either (1) our object detector or (2) the correlation trackers
	rects = []

	# check to see if we should run a more computationally expensive
	# object detection method to aid our tracker
	if totalFrames % conf["track_object"] == 0:
		# initialize our new set of object trackers
		trackers = []

		# convert the frame to a blob and pass the blob through the
		# network and obtain the detections
		blob = cv2.dnn.blobFromImage(frame, size=(300, 300),
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
				(startX, startY, endX, endY) = box.astype("int")


				# draws rectangle
				if endY < 370:
					cv2.rectangle(frame, (startX, startY), (endX, endY),(0, 255, 0), 2)

				
				# print("StartX & EndX", startX, endX)
				# print("StartY & EndY", startY, endY)


				# print("EndY", endY)
				
				# gets snapshot of vehicles
				#plt.imshow(frame[startY:endY,startX:endX], interpolation='nearest')
				#plt.show()
				
				if endY < 370:
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

			if endY < 370:
				cv2.rectangle(frame, (startX, startY), (endX, endY),(0, 255, 0), 2)
				# add the bounding box coordinates to the rectangles list
				rects.append((startX, startY, endX, endY))

	# use the centroid tracker to associate the (1) old object
	# centroids with (2) the newly computed object centroids
	objects = ct.update(rects)


	safe = True


	# print("Num cars: ", len(objects))
	if len(objects) == 0:
		num_zeros += 1
	else:
		num_zeros = 0

	if num_zeros == 2:
		# no more cars
		if counter == 1:
			print("Safe to Turn Left!")
			counter = 0
			num_zeros = 0

	# loop over the tracked objects
	for (objectID, centroid) in objects.items():
		# check to see if a trackable object exists for the current
		# object ID
		to = trackableObjects.get(objectID, None)

		# filt = pa.filters.FilterLMS(1, mu=2)

		# if there is no existing trackable object, create one
		if to is None:
			to = TrackableObject(objectID, centroid)
		
		# Note: centroid[i] = (cX, cY)
		
		to.distance = ds.distance_detection(to, centroid[1])
		# y = filt.predict(centroid[1])
		# filt.adapt(to.distance, centroid[1])

		if to.lastLoc == 0:
			# no last location recorded, so add and not calculate speed
			to.lastLoc = centroid[1]
		else:
			to.speed = ds.data_collection(to.lastLoc, centroid[1])
			if to.speed > 0: 
				if centroid[1] <= 360:
					safe = ss.safety_system(to.distance, to.speed)
					if not safe:
						if counter == 0:
							print("Not Safe to Turn Left!")
							counter = 1
					
						

					# print("[INFO] Speed of vehicle {:.2f}"\
					# " is: {:.2f} MPH".format(objectID, to.speedMPH))
					
					# print("[INFO] Distance of the vehicle {:.2f}"\
					# " is: {:.2f} feet".format(objectID, to.distance))

					# print("[INFO] Y-coord of the vehicle {:.2f}"\
					# " is: {:.2f}.".format(objectID, centroid[1]))
					
					# if objectID == 1:
						# print("[INFO] TOA of the vehicle {:.2f}"\
						# " is: {:.2f} seconds.".format(objectID, to.distance/to.speed))
						# print("[INFO] Speed of vehicle {:.2f}"\
						# " is: {:.2f}".format(objectID, to.speed))
						
						# print("[INFO] Distance of the vehicle {:.2f}"\
						# " is: {:.2f} feet".format(objectID, to.distance))
			else:
				None	

		# store the trackable object in our dictionary
		trackableObjects[objectID] = to

		# draw both the ID of the object and the centroid of the
		# object on the output frame
		text = "ID {}".format(objectID)
		cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10)
			, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		cv2.circle(frame, (centroid[0], centroid[1]), 4,
			(0, 255, 0), -1)
	
	
	# if the *display* flag is set, then display the current frame
	# to the screen and record if a user presses a key
	if conf["display"]:
		cv2.imshow("frame", frame)
		key = cv2.waitKey(1) & 0xFF

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

# close any open windows
cv2.destroyAllWindows()

# clean up
print("[INFO] cleaning up...")
vs.release()
