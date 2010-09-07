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
	def distanceto(p):
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
		return abs( (p2.x-p1.x)*(p1.y-p0.y) - (p1.x-p0.x)*(p2.y-p1.y) ) / p1.distancetopoiny(p2)





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
			if not self.ontheleft(punkt, self.points[i], self.points[(i+1)%l]):
				return False
		return True



#Koordinat som tupel av (X, Y, Z, t); X positiv österut, Y positiv norrut, Z positiv uppåt
k1 = (1234.0, 5678.0, 0, 1234.6)
k2 = (1240.0, 5689.0, 0, 1235.7)
k3 = (1246.0, 5678.0, 0, 1236.9)

#Område som lista av koordinater. Måste vara konvex och i högervarv
o1 = [(1224.0,5677.0), (1233.0,5698.0), (1244.0,5679.0), (1235.0,5668.0)]

#Linje, lista av exakt två koordinater
l1 = [o1[1], o1[2]]

coord1 = Coordinate(1234, 5678, 0, 1234.6)
coord2 = Coordinate(1240, 5689, 0, 1235.7)
coord3 = Coordinate(1246, 5678, 0, 1236.9)


corner1 = Coordinate(1224.0,5677.0)
corner2 = Coordinate(1233.0,5698.0)
corner3 = Coordinate(1244.0,5679.0)
corner4 = Coordinate(1235.0,5668.0)

poly1 = Polygon([corner1, corner2, corner3, corner4])


def distance(k1, k2):
	dx = abs(k1[0]-k2[0])
	dy = abs(k1[1]-k2[1])
	return sqrt(dx*dx+dy*dy)

def distancetoline(k, l):
	#http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
	p1 = l[0]
	p2 = l[1]
	return abs( (p2[0]-p1[0])*(p1[1]-k[1]) - (p1[0]-k[0])*(p2[1]-p1[1]) ) / distance(p1, p2)


def crossingtime(k1, k2, l):
	#http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
	x1 = k1[0]
	x2 = k2[0]
	x3 = l[0][0]
	x4 = l[1][0]
	y1 = k1[1]
	y2 = k2[1]
	y3 = l[0][1]
	y4 = l[1][1]

	t1 = k1[3]
	t2 = k2[3]

	d = ( (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1) )
	if d==0:
		ua = 0.5 #Linjerna parallella, gå på mitten för att undvika explosion
	else:
		ua = ( (x4-x3)*(y1-y3)-(y4-y3)*(x1-x3) ) / d

	#ua är "del av sträckan från k1 till k2". Om inte 0<=ua<=1 så korsar man inte linjen mellan k1 och k2
	#vilket betyder att man extrapolerar. Funkar det med.
	return t1+ua*(t2-t1)



def isinsidebounds(k, o):
	#Kontrollera att det finns både X- och Y-koordinater i området som är både större och mindre än punktens
	yl = yh = xl = xh = False

	for p in o:
		if p[0] >= k[0]: xh = True
		elif p[0] <= k[0]: xl = True
		if p[1] >= k[1]: yh = True
		elif p[1] <= k[1]: yl = True
		if xl and xh and yl and yh: break

	if not (xl and xh and yl and yh): return False

	return True


def ontheleft(p, p1,p2):
	v = p2[0]-p1[0], p2[1]-p1[1]
	n = v[1],-v[0]
	p = p[0]-p1[0], p[1]-p1[1]
	return (p[0]*n[0]+p[1]*n[1]) >= 0

def isinside(punkt, polygon):
	if not isinsidebounds(punkt, polygon): return False

	l = len(polygon)
	for i in range(l):
		if not ontheleft(punkt, polygon[i], polygon[(i+1)%l]):
			return False
	return True

def speed(k1, k2):
	return distance(k1, k2) / (k2[3] - k1[3])

def mstokmh(v):
	return 3.6*v


for i in range(int(sys.argv[1])):
#	foo = coord1.isinside(poly1)
#	bar = coord2.isinside(poly1)
#	baz = coord3.isinside(poly1)
	foo = isinside(k1, o1)
	bar = isinside(k2, o1)
	baz = isinside(k3, o1)

