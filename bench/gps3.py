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

class Vector:
	def __init__(self, p1, p2):
		if isinstance(p1, Coordinate): #A pair of coordinates
			self.x = p2.x-p1.x
			self.y = p2.y-p1.y
		else:
			self.x = float(p1)
			self.y = float(p2)

	def dot(self, v2):
		return self.x*v2.x+self.y*v2.y

	def normal(self):
		return Vector(self.y, -self.x)

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
	def __init__(self, vertices):
		self.vertices = vertices

		self.edges = []
		self.normals = []

		l = len(self.vertices)

		self.length = l

		self.xmax = self.xmin = self.vertices[0].x
		self.ymax = self.ymin = self.vertices[0].y

		for i in range(l):
			p1 = self.vertices[i]
			p2 = self.vertices[(i+1)%l]
			line = Line(p1, p2)
			self.edges.append(line)

			v = Vector(p1, p2)
			n = v.normal()
			self.normals.append(n)

			if p1.x > self.xmax: self.xmax = p1.x
			elif p1.x < self.xmin: self.xmin = p1.x
			if p1.y > self.ymax: self.ymax = p1.y
			elif p1.y < self.ymin: self.ymin = p1.y

	def isinsidebounds(self, p):
		
		if p.x > self.xmax: return False
		if p.x < self.xmin: return False
		if p.y > self.ymax: return False
		if p.y < self.ymin: return False

		return True

	def pointinside(self, punkt):
		if not self.isinsidebounds(punkt): return False

		for i in range(self.length):
			p = self.vertices[i]
			n = self.normals[i]
			v = Vector(p, punkt)
			if v.dot(n) < 0:
				return False
		return True

def mstokmh(v):
	return 3.6*v


coord1 = Coordinate(1234, 5678, 0, 1234.6)
coord2 = Coordinate(1240, 5689, 0, 1235.7)
coord3 = Coordinate(1246, 5678, 0, 1236.9)


corner1 = Coordinate(1224,5677)
corner2 = Coordinate(1233,5698)
corner3 = Coordinate(1244,5679)
corner4 = Coordinate(1235,5668)

poly1 = Polygon([corner1, corner2, corner3, corner4])

line1 = Line(corner2, corner3)


for i in range(int(sys.argv[1])):
#	foo = coord1.isinside(poly1)
#	bar = coord2.isinside(poly1)
#	baz = coord3.isinside(poly1)
	foo = poly1.pointinside(coord1)
	bar = poly1.pointinside(coord2)
	baz = poly1.pointinside(coord3)

