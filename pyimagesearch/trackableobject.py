# import the necessary packages
import numpy as np

class TrackableObject:
	def __init__(self, objectID, centroid):
		# store the object ID, then initialize a list of centroids
		# using the current centroid
		self.objectID = objectID
		self.centroids = [centroid] 
		self.lastLoc = 0 # this will store previous location
		self.distance = 0
		self.lastDist = 0

		self.lastPoint = False
		
		# initialize the object speeds in MPH and KMPH
		self.speedMPH = None
		self.speedKMPH = None

		# initialize the direction of the object
		self.direction = None
