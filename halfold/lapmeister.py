#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import gpsclient, convert, vector
import Queue
import time

import testgpsclient

import sys

def main(argv = None):

	if argv is None:
		argv = sys.argv[1:]

	#Starta GPS-läsaren
	gpsq = Queue.Queue()
#	gpsc = gpsclient.gpsclient(gpsq)
	gpsc = testgpsclient.gpsclient(gpsq)
	gpsc.start()

	c0 = None

	try:
		while 1:
			while not gpsq.empty():
				gpsevent = gpsq.get()
				(x, y) = convert.geodetic_to_grid(gpsevent['lat'], gpsevent['long'])
				gpsevent['x'] = x
				gpsevent['y'] = y
				print "Got gps event for %s at X%d Y%d" % (gpsevent['time_utc'], x, y)
				
				c1 = vector.Coordinate(x, y, gpsevent['time'], 0)
				

			time.sleep(0.1)

	except:
		gpsc.stop()

if __name__ == '__main__':
	sys.exit(main())
