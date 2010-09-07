#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import gpsclient, convert, vector, track
import Queue
import time, getopt

import testgpsclient

import sys

def log_gps_event(f, gpsevent):
	xml = '<coordinate'
	for item in gpsevent:
		xml += " %s=\"%s\"" % (item, gpsevent[item])
	xml += '/>\n'

	appendtolog(f, xml)
	
def log_checkpoint(f, transition, lap=0, id=""):
	x = transition.x
	y = transition.y
	z = transition.z
	t = transition.t

	xml = "<checkpoint lap=\"%d\" id=\"%s\" x=\"%f\" y=\"%f\" z=\"%f\" t=\"%f\"/>\n" % (lap, id, x, y, z, t)
	appendtolog(f, xml)


def log_sector(f, id, lap, time):
	xml = "<sector lap=\"%d\" id=\"%s\" time=\"%f\"/>\n" % (lap, id, time)
	appendtolog(f, xml)

def appendtolog(f, msg):
	if isinstance(f, file):
		f.write(msg)
	else:
		fp = open(f, "a")
		fp.write(msg)
		fp.close()

	

def event_to_coordinate(ev, tr):
	x = 0.0
	y = 0.0
	z = 0.0
	t = 0.0

	if not (('x' in ev) and ('y' in ev)):
		(x, y) = convert.geodetic_to_grid(ev['lat'], ev['long'])
		x += tr.offset_x
		y += tr.offset_y
		ev['x'] = x
		ev['y'] = y
	else:
		x = ev['x']
		y = ev['y']

	if 'z' in ev:
		z = float(ev['z'])
	elif 'altitude' in ev:
		z = float(ev['altitude'])

	if 'time' in ev:
		t_raw = float(ev['time'])
	elif 'time_utc' in ev:
		t_raw = float(ev['time_utc'])
	elif 't' in ev:
		t_raw = float(ev['t'])
	else:
		t_raw = time.time()

	try:
		t = float(t_raw)
	except ValueError:
		time_p = time.strptime(t_raw)
		t = float(time.mktime(time_p))

	c = vector.Coordinate(x,y,z,t)

	return c



	
LOG_ERROR = 0
LOG_WARNING = 4
LOG_INFO = 8
LOG_DEBUG = 12

loglevel = 8

def logmessage(message, msglevel = LOG_INFO):
	if msglevel > loglevel:
		return
	print message


def main(argv = None):

	global loglevel

	if argv is None:
		argv = sys.argv[1:]
		
	(optlist, args) = getopt.getopt(argv,"dq")

	for o, a in optlist:
		#Debug
		if o=="-d":
			if loglevel < LOG_DEBUG:
				loglevel = LOG_DEBUG
			else:
				loglevel += 1

		#Quiet. One q means "Just errors", more means even more silent
		if o=="-q":
			if loglevel > LOG_ERROR:
				loglevel = LOG_ERROR
			else:
				loglevel -= 1

	logmessage("Loglevel set to %d" % (loglevel), LOG_INFO+1)

	logmessage("Parsing track")

	tr = track.Track("track.xml")

	logmessage("Creating GPS")

	#Starta GPS-läsaren
	gpsq = Queue.Queue()
#	gpsc = gpsclient.gpsclient(gpsq)
	gpsc = testgpsclient.gpsclient(gpsq)
	time.sleep(0.5)
	logmessage("Starting GPS and logging")
	gpsc.start()
	
	c0 = None

	currentlap=0

	started_sectors ={}

	try:
		while 1:
			while not gpsq.empty():
				gpsevent = gpsq.get()

				log_gps_event("gpslog.txt", gpsevent)

				c1 = event_to_coordinate(gpsevent, tr)
				logmessage("Got gps event for %s at X%d Y%d" % (gpsevent['time_utc'], c1.x, c1.y), LOG_DEBUG+1)
				
				if not c0 is None:
					for wp in tr.waypoints:
						transition = wp.findTransition(c0, c1)
						if not transition is None:
							logmessage("Transition of %s at %.2f (%.2f, %.2f)" % (wp.name, transition.t, transition.x, transition.y), LOG_DEBUG)							
							log_checkpoint("checkpoints.txt", transition, currentlap, wp.id)

							for sec in tr.sectors:
								if sec.to_wp == wp.id and sec.id in started_sectors:
									#End of a sector that was previously started
									cstart = started_sectors[sec.id]
									tdiff = transition.t - cstart.t
									if sec.mintime <= 0.0 or tdiff > sec.mintime:
										logmessage("Sectortime for %s: %.2f" % (sec.name, tdiff), LOG_DEBUG)
										log_sector("sectors.txt", sec.id, currentlap, tdiff)
										if sec.id=="lap":
											logmessage("Finished lap %d in %.2f" % (currentlap, tdiff), LOG_DEBUG)
											currentlap += 1
										del started_sectors[sec.id]
									

								if sec.from_wp == wp.id:
									#Trigger start of a sector
									started_sectors[sec.id] = transition
									logmessage("Starting sector %s at %.2f" % (sec.name, transition.t), LOG_DEBUG)


			c0 = c1
			time.sleep(0.1)


#	except (KeyboardInterrupt, SystemExit, Exception), e:

	except:
		(etype, evalue, etraceback) = sys.exc_info()
		typename = etype.__name__
		if len(str(evalue))>0:
			valprefix = ": "
		else:
			valprefix = ""
			
		logmessage("Caught interrupt/exception (%s%s%s), exiting." % (typename, valprefix, evalue), LOG_ERROR)
		gpsc.stop()


if __name__ == '__main__':
	sys.exit(main())
