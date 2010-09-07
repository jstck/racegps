# -*- coding: utf-8 -*-

from xml import xpath
import xml.dom.minidom

import vector

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
	return vector.Coordinate(x, y, 0, 0)

def parseLine(lnode):
	coords = lnode.getElementsByTagName("coordinate")
	if len(coords)<2: return None
	p1 = parseCoordinate(coords[0])
	p2 = parseCoordinate(coords[0])
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

		doc = xml.dom.minidom.parse(filename)
		tracknode = doc.documentElement
#		doc = libxml2.parseFile(filename)

		self.name = getTextChild(doc, "name")
		self.length = float(getTextChild(doc, "length"))

#		print "Loading %s" % (self.name)

		self.waypoints = []
		waypoints = xpath.Evaluate("//track/waypoints/waypoint", doc)		
#		print "Found %d waypoints" % (len(waypoints))
		for wpnode in waypoints:
			wp = Waypoint(wpnode)
			self.waypoints.append(wp)
			print wp

		self.sectors = []
		sectors = xpath.Evaluate("//track/sectors/sector", doc)		
#		print "Found %d sectors" % (len(sectors))
		for sectornode in sectors:
			sector = Sector(sectornode)
			self.sectors.append(sector)
#			print sector

		self.zones = []
		zones = xpath.Evaluate("//track/zones/zone", doc)		
		print "Found %d zones" % (len(zones))
		for zonenode in zones:
			zone = Zone(zonenode)
			self.zones.append(zone)
#			print zone


	def __init__(self, filename):
		self.loadtrack(filename)




class Waypoint():
	def __init__(self, wpnode):

		self.name = wpnode.getAttribute("name")
		self.id = wpnode.getAttribute("id")

		linenode = xpath.Evaluate("line[1]", wpnode)[0]
		self.line = parseLine(linenode)


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

	def __str__(self):
		return "Waypoint %s (%s) " % (self.name, self.id) + str(self.line)


	def findTransition(self, c1, c2):
		if self.before.pointinside(c1) and self.after.pointinside(c2):
			transit = self.line.transit(c1, c2)
			speed = c1.speedto(c2)
			
			return (transit, speed)
			
		return None


class Sector():
	def __init__(self, sectornode):
		self.name = sectornode.getAttribute("name")
		self.id = sectornode.getAttribute("id")
		self.from_wp = sectornode.getAttribute("from")
		self.to_wp   = sectornode.getAttribute("to")		

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
