# -*- coding: utf-8 -*-
# encoding: utf-8

import time, Queue, threading

class gpsclient(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.running = False

		self.coords = []
		file = open("testvarv1.txt")
		for line in file.readlines():
			coords = line.split()
			for coord in coords:
				parts = coord.split(',')
				if len(parts)>=2:
					lat = float(parts[1])
					long = float(parts[0])
					c = [lat, long]
					self.coords.append(c)					

		self.i=0

	def stop(self):
		self.running = False

	def run(self):
		self.running = True

		while self.running:

			gpsdata = {}

			coord = self.coords[self.i]

			gpsdata['lat'] = coord[0]
			gpsdata['long'] = coord[1]
			gpsdata['time'] = self.i
			gpsdata['time_utc'] = self.i
			gpsdata['altitude'] = 17.0
			gpsdata['speed'] = 17.0

			self.queue.put(gpsdata)

			self.i += 1
			if self.i>=len(self.coords): self.i=0

			time.sleep(1.0)
