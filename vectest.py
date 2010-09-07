#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vector import *
from convert import *




pointlist = [Coordinate(6471959.597785, 1469780.662023),
	Coordinate(6471985.544059, 1469751.816192),
	Coordinate(6472021.968048, 1469759.317797),
	Coordinate(6472030.565693, 1469784.371302),
	Coordinate(6471978.234277, 1469804.638366)]
	
pointlist.reverse()

print pointlist

poly = Polygon(pointlist)


(x1, y1) = geodetic_to_grid(58.37041003870254,15.28869666790788)
(x2, y2) = geodetic_to_grid(58.37025375947504,15.28882225243603)
(x3, y3) = geodetic_to_grid(58.37008661682589,15.28883636200872)

p1 = Coordinate(x1, y1)
p2 = Coordinate(x2, y2)
p3 = Coordinate(x3, y3)

print poly

print "%s %d %d" % (p1, poly.isinsidebounds(p1), poly.pointinside(p1))
print "%s %d %d" % (p2, poly.isinsidebounds(p2), poly.pointinside(p2))
print "%s %d %d" % (p3, poly.isinsidebounds(p3), poly.pointinside(p3))
