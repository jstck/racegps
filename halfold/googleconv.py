#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, string, convert, getopt

if __name__ == '__main__':

	(optlist, args) = getopt.getopt(sys.argv[1:],"z:t")

	zstr=""
	tstr=""
	tick=False

	for o, a in optlist:
		if o=="-z":
			z=float(a)
			zstr = " z=\"%f\"" % (z)
			
		elif o=="-t":
			tick = True
			t = 1
	
	print optlist
	print zstr

	for line in sys.stdin.readlines():
		coords = line.split()
		for coord in coords:
			parts = coord.split(',')
			if len(parts)>=2:
				long = float(parts[0])
				lat = float(parts[1])
				(x, y) = convert.geodetic_to_grid(lat, long)
				
				if tick:
					tstr=" t=\"%d\"" % (t)
					t+=1
				
				print "<coordinate x=\"%f\" y=\"%f\"%s%s>" % (x, y, zstr, tstr)
