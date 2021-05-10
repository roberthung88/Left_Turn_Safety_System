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

		self.speed = 0
		
		# initialize the direction of the object
		self.direction = None
