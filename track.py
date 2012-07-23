# -*- coding: utf-8 -*-

#from xml import xpath
#import xml.dom.minidom

import libxml2

import vector, convert

#Get the text content of a node by just concatenating all text children
def textContent(node):
	txt = ""
	for child in node.childNodes:
		if child.nodeType == child.TEXT_NODE:
			txt = txt + child.nodeValue
	return txt

#Hämta innehållet i en text-undernod med visst namn
def getTextChild(node, nodename):
	nodes = node.getElementsByTagName(nodename)
	if len(nodes) >= 1:
		return textContent(nodes[0])

	return None


def parseCoordinate(cnode):
	x = float(cnode.getAttribute("x"))
	y = float(cnode.getAttribute("y"))

	if cnode.hasAttribute("z"):
		z = float(cnode.getAttribute("z"))
	elif cnode.hasAttribute("altitude"):
		z = float(cnode.getAttribute("altitude"))
	else:
		z = 0.0

	if cnode.hasAttribute("t"):
		t = float(cnode.getAttribute("t"))
	elif cnode.hasAttribute("time_utc"):
		t = float(cnode.getAttribute("time_utc"))
	else:
		t = 0.0
		
	return vector.Coordinate(x, y, z, t)

def parseLine(lnode):
	coords = lnode.getElementsByTagName("coordinate")
	if len(coords)<2: return None
	p1 = parseCoordinate(coords[0])
	p2 = parseCoordinate(coords[1])
	return vector.Line(p1, p2)

def parsePolygon(pnode):
	coords = pnode.getElementsByTagName("coordinate")
	if len(coords)<2: return None
	clist = []
	for coord in coords:
		c = parseCoordinate(coord)
		clist.append(c)
	return vector.Polygon(clist)

class Track():
	
	def loadtrack(self, filename):

		doc = libxml2.parseFile(filename)
		tracknode = doc.documentElement
#		doc = libxml2.parseFile(filename)

		self.name = getTextChild(doc, "name")
		self.length = float(getTextChild(doc, "length"))

#		print "Loading %s" % (self.name)

		self.offset_x = 0.0
		self.offset_y = 0.0
		
		offset = xpath.Evaluate("//track/offset", doc)
		if len(offset)>=1:
			offset = offset[0]
			if offset.hasAttribute("x"): self.offset_x = float(offset.getAttribute("x"))
			if offset.hasAttribute("y"): self.offset_y = float(offset.getAttribute("y"))
			
#		print "Offset X %f Y %f" % (self.offset_x, self.offset_y)
			
		self.waypoints = []
		waypoints = xpath.Evaluate("//track/waypoints/waypoint", doc)		
#		print "Found %d waypoints" % (len(waypoints))
		for wpnode in waypoints:
			wp = Waypoint(wpnode)
			self.waypoints.append(wp)
#			print wp

		self.sectors = []
		sectors = xpath.Evaluate("//track/sectors/sector", doc)		
#		print "Found %d sectors" % (len(sectors))
		for sectornode in sectors:
			sector = Sector(sectornode)
			self.sectors.append(sector)
#			print sector

		self.zones = []
		zones = xpath.Evaluate("//track/zones/zone", doc)		
#		print "Found %d zones" % (len(zones))
		for zonenode in zones:
			zone = Zone(zonenode)
			self.zones.append(zone)
#			print zone


	def __init__(self, filename):
		self.loadtrack(filename)
		
		
			

def polygon_js(coords, color, width):
	js = "var polyline = new GPolyline([\n"
	firstcoord = None
	for coord in coords:
		(lat, long) = convert.grid_to_geodetic(coord.x, coord.y)
		cjs = "new GLatLng(%f, %f),\n" % (lat, long);
		if firstcoord is None:
			firstcoord = cjs
		js += cjs
	
	js += firstcoord
	
	js += "], \"%s\", %d);\n" % (color, width)
	js += "map.addOverlay(polyline);"
	
	return js
	
def track_to_js(track):
	js = "function drawTrack(map) {\n"
	for wp in track.waypoints:
		coords = [ wp.line.p1, wp.line.p2 ]
		js += polygon_js(coords, "#FF0000", 4)
		
		coords = wp.before.vertices
		js += polygon_js(coords, "#7777FF", 3)

		coords = wp.after.vertices
		js += polygon_js(coords, "#77FF77", 3)
	
	js += "\n}";
	
	return js


class Waypoint():
	def __init__(self, wpnode):

		self.name = wpnode.getAttribute("name")
		self.id = wpnode.getAttribute("id")

		linenode = xpath.Evaluate("line", wpnode)[0]
		self.line = parseLine(linenode)

		self.before = None
		self.after = None

		beforenode = xpath.Evaluate('zone[@id="before"]/*[1]', wpnode)[0]
		afternode = xpath.Evaluate('zone[@id="after"]/*[1]', wpnode)[0]

		#Construct polygons for "before" and "after" zones in different fashions.
		#First two elements in polygon correspond to the line (for no obvious reason)
		#Polygons must be kept right-handed
		i = 0

		for zone in [beforenode, afternode]:		
			if zone.nodeName == "polygon":
				poly = parsePolygon(zone)
			elif zone.nodeName == "width":
				width = float(textContent(zone))
				lnorm = self.line.vector().normal().unit() * width

				#Construct zone differently if it is before or after (different sides of line, different directions)
				if i==0:
					p3 = self.line.p1 + lnorm
					p4 = self.line.p2 + lnorm
					poly = vector.Polygon([self.line.p1, self.line.p2, p4, p3])
				else:
					p3 = self.line.p1 - lnorm
					p4 = self.line.p2 - lnorm
					poly = vector.Polygon([self.line.p2, self.line.p1, p3, p4])

			elif zone.nodeName == "line":
				l2 = parseLine(zone)

				#Different directions to keep polygon right-handed
				if i==0:
					poly = vector.Polygon([self.line.p1, self.line.p2, l2.p2, l2.p1])
				else:
					poly = vector.Polygon([self.line.p2, self.line.p1, l2.p1, l2.p2])

			else: #UNKNOWN!
				return None	

			if i==0:
				self.before = poly
			else:
				self.after = poly

			i += 1

	def __str__(self):
		return "Waypoint %s (%s) " % (self.name, self.id) + str(self.line)


	def findTransition(self, c1, c2):
#		if self.before.pointinside(c2): print "Hit before: %s" % (self.name)
#		if self.after.pointinside(c2): print "Hit after:  %s" % (self.name)
			
		if self.before.pointinside(c1) and self.after.pointinside(c2):
			return self.line.transit(c1, c2)
			
		return None


class Sector():
	def __init__(self, sectornode):
		self.name = sectornode.getAttribute("name")
		self.id = sectornode.getAttribute("id")
		self.from_wp = sectornode.getAttribute("from")
		self.to_wp   = sectornode.getAttribute("to")
		self.mintime = -1.0
		if sectornode.hasAttribute("mintime"):
			self.mintime = float(sectornode.getAttribute("mintime"))

	def __str__(self):
		return "Sector %s (%s) from %s to %s" % (self.name, self.id, self.from_wp, self.to_wp)

class Zone():
	def __init__(self, zonenode):
		self.name = zonenode.getAttribute("name")
		self.id = zonenode.getAttribute("id")
		polynode = zonenode.getElementsByTagName("polygon")[0]
		self.polygon = parsePolygon(polynode)
		
	def __str__(self):
		return "Zone %s (%s)" % (self.name, self.id)

if __name__ == '__main__':
	track = Track("track.xml")
	print track_to_js(track)
