# -*- coding: utf-8 -*-
# encoding: utf-8

import gps, time, Queue, threading

class gpsclient(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.session = gps.gps()
		self.running = False

	def stop(self):
		self.running = False

	def run(self):
		self.running = True
		session = self.session
		lasttime = 0
		while self.running:

  	  # a = altitude, d = date/time, m=mode,
	    # o=postion/fix, s=status, y=satellites
			session.query('admos')
			if session.fix.time == lasttime:
				#No new updates
				continue

			gpsdata = {}
			gpsdata['lat'] = session.fix.latitude
			gpsdata['long'] = session.fix.longitude
			gpsdata['time'] = session.fix.time
			gpsdata['time_utc'] = session.utc
			gpsdata['altitude'] = session.fix.altitude
			gpsdata['speed'] = session.fix.speed
			# session.fix.eph
			# session.fix.epv
			# session.fix.ept
			# session.fix.speed
			# session.fix.climb
			# for i in session.satellites

			self.queue.put(gpsdata)

			lasttime = session.fix.time

			time.sleep(0.5)

