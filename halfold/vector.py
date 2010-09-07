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

	def __mul__(self, v2):
		if isinstance(v2, Vector):
			#Vector * Vector => dot product
			return self.x*v2.x+self.y*v2.y
		else:
			#Vector * scalar => scale
			v2=float(v2)
			return Vector(self.x*v2, self.y*v2)

	def __add__(self, v2):
		return Vector(self.x+v2.x, self.y+v2.y)

	def __sub__(self, v2):
		return Vector(self.x-v2.x, self.y-v2.y)

	def __neg__(self):
		return self * -1

	def normal(self):
		return Vector(self.y, -self.x)

	def length(self):
		return sqrt(self.x**2 + self.y**2)

	def unit(self):
		l = self.length()
		if(l==0): return Vector(0, 0)
		return Vector(self.x/l, self.y/l)

	def __str__(self):
		return "[%.3f %.3f]" % (self.x, self.y)

class Coordinate:
	def __init__(self, x, y, z=0, t=0):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
		self.t = float(t)

	def __str__(self):
		return "(%.3f %.3f)" % (self.x, self.y)

	def dump(self):
		return str(self.x) + " " + str(self.y) + " " + str(self.z) + " " + str(self.t)

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
		return sqrt(dx**2+dy**2)

	def speedto(self, p):
		if p.t - self.t == 0: return 10000 #Infinite speed!
		return self.distancetopoint(p) / (p.t - self.t)

	def distance(p1, p2):
		return p1.distancetopoint(p2)
	distance = Callable(distance)

	def speed(p1, p2):
		return p1.speedto(p2)
	speed = Callable(speed)

	def translate(self, v, scale=1.0):
		return Coordinate(self.x + scale*v.x, self.y + scale*v.y)

	def __sub__(self, v):
		if isinstance(v, Vector):
			return Coordinate(self.x-v.x, self.y-v.y, self.z, self.t)
		elif isistance(v, Coordinate):
			return Vector(self.x-v.x, self.y-v.y)
		else:
			raise TypeError, "Invalid type"
			return None

	def __add__(self, v):
		if not isinstance(v, Vector):
			raise TypeError, "Invalid type"
			return None
		
		return Coordinate(self.x+v.x, self.y+v.y, self.z, self.t)

class Line:
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2

	def __str__(self):
		return "(%.3f %.3f) - (%.3f %.3f)" % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

	def length(self):
		return self.p1.distancetopoint(p2)

	#Distance to a point
	def distanceto(self, p0):
		#http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
		p1 = self.p1
		p2 = self.p2
		return abs( (p2.x-p1.x)*(p1.y-p0.y) - (p1.x-p0.x)*(p2.y-p1.y) ) / p1.distancetopoint(p2)

	#Check if p is to the left of the line
	def ontheleft(self,p):
		return ((p.x-self.p1.x)*(self.p2.y-self.p1.y)+(p.y-self.p1.y)*(self.p1.x-self.p2.x)) >= 0

	def vector(self):
		return Vector(self.p2.x-self.p1.x, self.p2.y-self.p1.y)

	#Coordinate and time when line is crossed, given two points (in space and time)
	#Assumes linear motion.
	def transit(self, p1, p2):
		#http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/

		p3 = self.p1
		p4 = self.p2

		d = ( (p4.y-p3.y)*(p2.x-p1.x)-(p4.x-p3.x)*(p2.y-p1.y) )
		if d==0:
			ua = 0.5 #Lines parallel, use median value to avoid explosion
		else:
			ua = ( (p4.x-p3.x)*(p1.y-p3.y)-(p4.y-p3.y)*(p1.x-p3.x) ) / d

		#ua is "part ov distance from p1 to p2. If not 0<=ua<=1 then line is crossed
		#outside the interval. Extrapolation works too.
		x = p1.x+ua*(p2.x-p1.x)
		y = p1.y+ua*(p2.y-p1.y)
		z = p1.z+ua*(p2.z-p1.z)
		t = p1.t+ua*(p2.t-p1.t)

		return Coordinate(x,y,z,t)

	#Check how a point is in relation to line
	# <0: p to left of line
	# =0: p on the line
	# >0: p to the right of line
	def pointlocation(self, p):

		v = Vector(self.p1, self.p2)
		n = v.normal()

		v2 = Vector(self.p1, p)
		return v2*n




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
			if v*n < 0: #samma returvärde som Line.pointlocation()
				return False
		return True

def mstokmh(v):
	return 3.6*v


