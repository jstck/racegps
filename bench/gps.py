#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import string
import sys
import re
from math import *


class Callable:
	def __init__(self, anycallable):
		self.__call__ = anycallable


class Coordinate:
	def __init__(self, x, y, z=0, t=0):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
		self.t = float(t)


	#Distance to a point or a line
	def distanceto(self, p):
		if isinstance(p, Coordinate):
			return self.distancetopoint(p)
		elif isinstance(p, Line):
			return p.distanceto(self)

	def isinside(self, polygon):
		return polygon.pointinside(self)

	def distancetopoint(self, p):
		dx = abs(self.x - p.x)
		dy = abs(self.y - p.y)
		return sqrt(dx*dx+dy*dy)

	def speedto(self, p):
		if p.t - self.t == 0: return 10000 #Infinite speed!
		return self.distancetopoint(p) / (p.t - self.t)

	def distance(p1, p2):
		return p1.distancetopoint(p2)
	distance = Callable(distance)

	def speed(p1, p2):
		return p1.speedto(p2)
	speed = Callable(speed)




class Line:
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2

	def length(self):
		return self.p1.distancetopoint(p2)

	#Distance to a point
	def distanceto(self, p0):
		#http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
		p1 = self.p1
		p2 = self.p2
		return abs( (p2.x-p1.x)*(p1.y-p0.y) - (p1.x-p0.x)*(p2.y-p1.y) ) / p1.distancetopoint(p2)

	#Kontrollera om p ligger till vänster om linjen
	def ontheleft(self,p):
		return ((p.x-self.p1.x)*(self.p2.y-self.p1.y)+(p.y-self.p1.y)*(self.p1.x-self.p2.x)) >= 0


	#Time when a line is crossed, given two points (assuming linear motion between points)
	def crossingtime(self, p1, p2):
		#http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/

		p3 = self.p1
		p4 = self.p2

		d = ( (p4.y-p3.y)*(p2.x-p1.x)-(p4.x-p3.x)*(p2.y-p1.y) )
		if d==0:
			ua = 0.5 #Linjerna parallella, gå på mitten för att undvika explosion
		else:
			ua = ( (p4.x-p3.x)*(p1.y-p3.y)-(p4.y-p3.y)*(p1.x-p3.x) ) / d

		#ua är "del av sträckan från k1 till k2". Om inte 0<=ua<=1 så korsar man inte linjen mellan k1 och k2
		#vilket betyder att man extrapolerar. Funkar det med.
		return p1.t+ua*(p2.t-p1.t)



class Polygon:
	def __init__(self, points = []):
		self.points = points

	def addpoint(self, p):
		self.points.append(p)


	def isinsidebounds(self, k):
		#Kontrollera att det finns både X- och Y-koordinater i polygonen som är både större och mindre än punktens
		yl = yh = xl = xh = False

		for p in self.points:
			if p.x >= k.x: xh = True
			elif p.x <= k.x: xl = True
			if p.y >= k.y: yh = True
			elif p.y <= k.y: yl = True
			if xl and xh and yl and yh: return True

		return False

	#Kontrollera om p ligger till vänster om linjen från p1 till p2
	def ontheleft(p, p1,p2):
#  	vx = p2.x-p1.x
#		vy = p2.y-p1.y
#	  nx = v.y
#		ny = -v.x		
#	  p = p.x-p1.x, p.y-p1.y
#	  return (p.x*nx+p.y*ny) >= 0
		return ((p.x-p1.x)*(p2.y-p1.y)+(p.y-p1.y)*(p1.x-p2.x)) >= 0
	ontheleft = Callable(ontheleft)

	def pointinside(self, punkt):
		if not self.isinsidebounds(punkt): return False

		l = len(self.points)
		for i in range(l):
			line = Line(self.points[i], self.points[(i+1)%l])
			if not line.ontheleft(punkt):
				return False
		return True

	def pointinside2(self, punkt):
		if not self.isinsidebounds(punkt): return False

		l = len(self.points)
		for i in range(l):
			p1 = self.points[i]
			p2 = self.points[(i+1)%l]

			line = Line(self.points[i], self.points[(i+1)%l])

			if ((p.x-p1.x)*(p2.y-p1.y)+(p.y-p1.y)*(p1.x-p2.x)) < 0:
				return False

		return True


def mstokmh(v):
	return 3.6*v


coord1 = Coordinate(1234, 5678, 0, 1234.6)
coord2 = Coordinate(1240, 5689, 0, 1235.7)
coord3 = Coordinate(1246, 5678, 0, 1236.9)


corner1 = Coordinate(1224.0,5677.0)
corner2 = Coordinate(1233.0,5698.0)
corner3 = Coordinate(1244.0,5679.0)
corner4 = Coordinate(1235.0,5668.0)

poly1 = Polygon([corner1, corner2, corner3, corner4])

line1 = Line(corner2, corner3)

for i in range(int(sys.argv[1])):
	foo = coord1.isinside(poly1)
	bar = coord2.isinside(poly1)
	baz = coord3.isinside(poly1)
#	foo = poly1.pointinside(coord1)
#	bar = poly1.pointinside(coord2)
#	baz = poly1.pointinside(coord3)

