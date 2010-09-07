#!/usr/bin/env python
# -*- coding: utf-8 -*-


#Originally from http://mellifica.se/geodesi/gausskruger.js
#Author: Arnold Andreasson, 2007. http://mellifica.se/konsult
#License: http://creativecommons.org/licenses/by-nc-sa/3.0/

#Adapted to python by John Stäck 2009, john@stack.se


import math

#Union of two dictionaries, elements in d2 overwrites d1
def dict_union(d1, d2):
	union = {}
	for e in d1:
		union[e] = d1[e]
	for e in d2:
		union[e] = d2[e]
	return union

params_sweref99 = {
	'axis': 6378137.0,
	'flattening': 1.0/298.257222101,
	'central_meridian': 0.0,
	'lat_of_origin': 0.0,
	'scale': 1.0,
	'false_northing': 0.0,
	'false_easting': 150000.0
}

params_sweref99_tm = dict_union(params_sweref99,
	{
		'central_meridian': 15.00,
		'lat_of_origin': 0.0,
		'scale': 0.9996,
		'false_northing': 0.0,
		'false_easting': 500000.0
	}
)


params_grs80 = {
	'axis': 6378137.0,
	'flattening': 1.0/298.257222101,
	'central_meridian': 0.0,
	'lat_of_origin': 0.0
}

#One kind if RT90 2.5 gon V, from original source. Based on GRS80 ellipsoid. Noone uses bessel 1841.
#Seems to be the right one when checking against other sources (such as kartor.eniro.se)
params_rt90_25V = dict_union(params_grs80,
	{
		'central_meridian': 15.0 + 48.0/60.0 + 22.624306/3600.0,
		'scale': 1.00000561024,
		'false_northing': -667.711,
		'false_easting':  1500064.274
	}
)

#Another kind of RT 90 2.5 gon V 0:-15
#from http://www.lantmateriet.se/templates/LMV_Page.aspx?id=4766
params_rt90_25V_LM = {
	'axis': 6377397.155,
	'flattening': 1.0/299.1528128,
	'central_meridian': 15.0 + 48.0/60 + 29.8/3600, #15°48'29".8 Ö
	'lat_of_origo': 0.0,
	'scale': 1.0,
	'false_northing': 0.0,
	'false_easting': 1500000.0
}

#Do precalculations of used constants for ellipsoid
def precalc(params):
	e2 = params['flattening'] * (2.0 - params['flattening'])
	n = params['flattening'] / (2.0 - params['flattening'])
	a_roof = params['axis'] / (1.0 + n) * (1.0 + n**2/4.0 + n**4/64.0)
	A = e2
	B = (5.0*e2**2 - e2**3) / 6.0
	C = (104.0*e2**3 - 45.0*e2**4) / 120.0
	D = (1237.0*e2**4) / 1260.0
	beta1 = n/2.0 - 2.0*n**2/3.0 + 5.0*n**3/16.0 + 41.0*n**4/180.0
	beta2 = 13.0*n**2/48.0 - 3.0*n**3/5.0 + 557.0*n**4/1440.0
	beta3 = 61.0*n**3/240.0 - 103.0*n**4/140.0
	beta4 = 49561.0*n**4/161280.0

	delta1 = n/2.0 - 2.0*n**2/3.0 + 37.0*n**3/96.0 - n**4/360.0
	delta2 = n**2/48.0 + n**3/15.0 - 437.0*n**4/1440.0
	delta3 = 17.0*n**3/480.0 - 37*n**4/840.0
	delta4 = 4397.0*n**4/161280.0
	
	Astar = e2 + e2*e2 + e2*e2*e2 + e2*e2*e2*e2
	Bstar = -(7.0*e2*e2 + 17.0*e2*e2*e2 + 30.0*e2*e2*e2*e2) / 6.0
	Cstar = (224.0*e2*e2*e2 + 889.0*e2*e2*e2*e2) / 120.0
	Dstar = -(4279.0*e2*e2*e2*e2) / 1260.0	

	params['e2'] = e2
	params['n'] = n
	params['a_roof'] = a_roof
	params['A'] = A
	params['B'] = B
	params['C'] = C
	params['D'] = D
	params['beta1'] = beta1
	params['beta2'] = beta2
	params['beta3'] = beta3
	params['beta4'] = beta4
	params['delta1'] = delta1
	params['delta2'] = delta2
	params['delta3'] = delta3
	params['delta4'] = delta4
	params['Astar'] = Astar
	params['Bstar'] = Bstar
	params['Cstar'] = Cstar
	params['Dstar'] = Dstar
	params['precalc'] = True

#Define inverse hyperbolic functions, not in python 2.5
def asinh(x):
	return math.log(x + math.sqrt(x*x+1))
def acosh(x):
	return math.log(x + math.sqrt(x-1) + math.sqrt(x+1))
def atanh(x):
	return 0.5 * math.log((1+x)/(1-x))

#Degrees to radians and back
def deg2rad(deg):
	return math.pi / 180 * deg
def rad2deg(rad):
	return 180.0 / math.pi * rad

#Convert degree,minute,second to just degree
def dmstodeg(d, m, s):
	if d >= 0:
		return float(d) + float(m) / 60.0 + float(s) / 3600.0
	else:
		#If d is negative, so are m and s implicitly
		return float(d) - float(m) / 60.0 - float(s) / 3600.0

#Convert lat/long to grid coordinates, transverse mercator projection according to a specific
#parameter set
def geodetic_to_grid(latitude, longitude, params=params_rt90_25V):
	
	#Make sure precalculated values are precalculated.
	if not 'precalc' in params:
		precalc(params)
	
	#Is this where lat_of_origin goes? Always set to 0.0, never used. Plus or minus?
	#latitude = latitude + params['lat_of_origin']
	
	#Convert
	phi = deg2rad(latitude)
	sin_phi = math.sin(phi)
	cos_phi = math.cos(phi)
	lambdaL = deg2rad(longitude) #'lambda' is reserved
	lambda_zero = deg2rad(params['central_meridian'])
	phi_star = phi - sin_phi * cos_phi * (params['A'] +
		params['B'] * sin_phi**2 +
		params['C'] * sin_phi**4 +
		params['D'] * sin_phi**6)
	delta_lambda = lambdaL - lambda_zero
	xi_prim = math.atan(math.tan(phi_star) / math.cos(delta_lambda))
	eta_prim = atanh(math.cos(phi_star) * math.sin(delta_lambda))
	x = params['scale'] * params['a_roof'] * (
			xi_prim +
			params['beta1'] * math.sin(2.0*xi_prim) * math.cosh(2.0*eta_prim) +
			params['beta2'] * math.sin(4.0*xi_prim) * math.cosh(4.0*eta_prim) +
			params['beta3'] * math.sin(6.0*xi_prim) * math.cosh(6.0*eta_prim) +
			params['beta4'] * math.sin(8.0*xi_prim) * math.cosh(8.0*eta_prim)
		) + params['false_northing']
	y = params['scale'] * params['a_roof'] * (
			eta_prim +
			params['beta1'] * math.cos(2.0*xi_prim) * math.sinh(2.0*eta_prim) +
			params['beta2'] * math.cos(4.0*xi_prim) * math.sinh(4.0*eta_prim) +
			params['beta3'] * math.cos(6.0*xi_prim) * math.sinh(6.0*eta_prim) +
			params['beta4'] * math.cos(8.0*xi_prim) * math.sinh(8.0*eta_prim)
		) + params['false_easting']

	return (x,y)
	
	


def grid_to_geodetic(x, y, params=params_rt90_25V):
	#Make sure precalculated values are precalculated.
	if not 'precalc' in params:
		precalc(params)
		
	#Convert.
	lambda_zero = deg2rad(params['central_meridian'])
	xi = (x - params['false_northing']) / (params['scale'] * params['a_roof'])		
	eta = (y - params['false_easting']) / (params['scale'] * params['a_roof'])
	xi_prim = xi - (
		params['delta1']*math.sin(2.0*xi) * math.cosh(2.0*eta) - 
		params['delta2']*math.sin(4.0*xi) * math.cosh(4.0*eta) - 
		params['delta3']*math.sin(6.0*xi) * math.cosh(6.0*eta) - 
		params['delta4']*math.sin(8.0*xi) * math.cosh(8.0*eta)
	)
	eta_prim = eta - (
		params['delta1']*math.cos(2.0*xi) * math.sinh(2.0*eta) - 
		params['delta2']*math.cos(4.0*xi) * math.sinh(4.0*eta) - 
		params['delta3']*math.cos(6.0*xi) * math.sinh(6.0*eta) - 
		params['delta4']*math.cos(8.0*xi) * math.sinh(8.0*eta)
	)
	phi_star = math.asin(math.sin(xi_prim) / math.cosh(eta_prim))
	delta_lambda = math.atan(math.sinh(eta_prim) / math.cos(xi_prim))
	lon_radian = lambda_zero + delta_lambda
	lat_radian = phi_star + math.sin(phi_star) * math.cos(phi_star) * (
		params['Astar'] + 
		params['Bstar']*math.sin(phi_star)**2 + 
		params['Cstar']*math.sin(phi_star)**4 + 
		params['Dstar']*math.sin(phi_star)**6
	) 
	lat = rad2deg(lat_radian)
	lon = rad2deg(lon_radian)
	return (lat, lon)

if __name__ == '__main__':
	print """

Sergelpinnen, http://kartor.eniro.se/m/M3xC2
WGS 84:N 59° 19.954', E 18° 3.910'
WGS 84 - decimal:59.33257, 18.06516
RT90: 6581267, 1628625
SWEREF99: 6581098, 674360
"""

	lat = dmstodeg(59, 19.954, 0)
	long = dmstodeg(18, 3.910, 0)

	rt90 = geodetic_to_grid(lat, long)
	sw99 = geodetic_to_grid(lat, long, params_sweref99_tm)

	print "N %.6f E %.6f" % (lat, long)
	print "X %.0f Y %.0f (RT90)" % rt90
	print "X %.0f Y %.0f (SWEREF99)" % sw99
	print "N %.6f E %.6f" % grid_to_geodetic(rt90[0], rt90[1])
	print "N %.6f E %.6f" % grid_to_geodetic(sw99[0], sw99[1], params_sweref99_tm)

	print
	lat = 59.33257
	long = 18.06516
	rt90 = geodetic_to_grid(lat, long)
	sw99 = geodetic_to_grid(lat, long, params_sweref99_tm)

	print "N %.6f E %.6f" % (lat, long)
	print "X %.0f Y %.0f (RT90)" % rt90
	print "X %.0f Y %.0f (SWEREF99)" % sw99
	print "N %.6f E %.6f" % grid_to_geodetic(rt90[0], rt90[1])
	print "N %.6f E %.6f" % grid_to_geodetic(sw99[0], sw99[1], params_sweref99_tm)

