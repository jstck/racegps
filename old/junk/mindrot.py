#!/usr/bin/env python

import os, sys, socket, string, select, re, getopt, time

def usage():
	print "gps.py 0.01 commandline mode. Available options:"
	print "         -h      Display this help"
	print "         -d      Turn on debugging"
	print "         -l      Turn on logging mode"
	print "If executed without any arguments, gps.py will query a local "
	print "gpsd (on port 2947) and display the results. "
	print ""
	print "If placed in logging mode (-l option), gps.py will poll the "
	print "gpsd every second and print the time (UTC secs-since-epoch), "
	print "GPS status altitude and location separated by spaces until "
	print "interrupted."
	sys.exit(0)
		
class GPS:
	"""Manage a connection to a GPS device (as represented by gpsd)"""
	
	def __init__(self, host = '127.0.0.1', port = 2947, debug = 0):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, port))
		self.debug = debug
		self.data = {}
		self.update()

	def __del__(self):
		# Close socket gracefully
		self.sock.close()

	def update(self):
		"""Fetch the latest status from gpsd"""
		self.sock.send("PDAVSM")
		result = self.sock.recv(2048)
		result = result[:-1].rstrip()
		if self.debug == 1:
			print >> sys.stderr, ">GPSD: PDAVSM" 
			print >> sys.stderr, "GPSD>: %s" % result
		chunks = string.split(result, ',')
		if chunks[0] != "GPSD":
			return
		for chunk in chunks[1:]:
			self.data[chunk[0]] = string.split(chunk[2:], ' ')

	def position(self):
		"""Return latest latitude/longitude position array"""
		return (float(self.data['P'][0]), float(self.data['P'][1]))

	def altitude(self):
		"""Return latest altitude (meters)"""
		return float(self.data['A'][0])

	def velocity(self):
		"""Return latest velocity (knots)"""
		return float(self.data['V'][0])

	def status(self, text = 0):
		"""Return latest GPS status"""
		status = int(self.data['S'][0])
		if text:
			return ('NONE', 'GPS', 'dGPS')[status]
		else:
			return status

	def mode(self, text = 0):
		"""Return latest mode"""
		mode = int(self.data['M'][0])
		if text:
			return ('NO-FIX', '2D-FIX', '3D-FIX')[mode - 1]
		else:
			return mode

	def time(self):
		"""Return GPS time of last sample (UTC, secs-since-epoch)"""
		try:
			jtime = string.join(self.data['D'], ' ')
			tm = time.strptime(jtime, '%m/%d/%Y %H:%M:%S')
		except ValueError:
			return 0

		return int(time.mktime(tm) + 0.5)

def main():
	debug = 0
	logmode = 0
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hdl', \
		    ['help', 'debug', 'log'])
	except getopt.GetoptError:
		print >> sys.stderr, "Invalid commandline arguments"
		usage()
		sys.exit(1)

	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit(0)
		if o in ('-d', '--debug'):
			debug = 1
			continue
		if o in ('-l', '--log'):
			logmode = 1
			continue

	try:
		gps = GPS(debug = debug)
	except socket.error, (errno, strerror):
		print >> sys.stderr, "Couldn't connect to gpsd: " + strerror
		sys.exit(1)

	if not logmode:
		print "Time: " ,
		print gps.time()
		print "Position: " ,
		print gps.position()
		print "Altitude: " ,
		print gps.altitude()
		print "Velocity: " ,
		print gps.velocity()
		print "Status: " ,
		print gps.status()
		print "Mode: " ,
		print gps.mode()
		print ""
		sys.exit(0)
	
	print "#Time Status Altitude Latitude Longitude"
	try:
		while 1:
			gps.update()
			print "%d %s %0.8f %0.8f %0.8f" % \
			    (gps.time(), gps.mode(1), gps.altitude(), \
			     gps.position()[0], gps.position()[1])
			sys.stdout.flush()
			time.sleep(1) 
	except KeyboardInterrupt:
		del gps
		sys.exit(0)
	except IOError:
		del gps
		sys.exit(0)
		
if __name__ == '__main__': main()

