#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

from math import *

def deg2rad(deg):
	return pi / 180 * deg

def rad2deg(rad):
	return 180.0 / pi * rad

def convert(latitude, longitude, datum="RT90"):

	if type(latitude)==tuple or type(latitude)==list:
		degs = latitude[0]
		mins = latitude[1]
		secs = latitude[2]
		latitude = degs + mins * 1.0/60 + secs * 1.0/3600
	if type(longitude)==tuple or type(longitude)==list:
		degs = longitude[0]
		mins = longitude[1]
		secs = longitude[2]
		longitude = degs + mins * 1.0/60 + secs * 1.0/3600

	K=deg2rad(latitude)
	L=deg2rad(longitude)

	#SWEREF93/RT90
	if(datum=="SWEREF93"):
		F0=1.00000564631
		A1=6378137.0*F0
		B1=6356752.3*F0
		K0=0.0
		Merid=15.8062819
		L0=deg2rad(Merid)
		N0=-667.968
		E0=1500064.08


	#RT90
	else: #if(datum=="RT90"):
		F0=1.0
		A1=6377397.155*F0
		B1=6356078.963*F0
		K0=0.0
		Merid=15.8082777778
		L0=deg2rad(Merid)
		N0=0.0
		E0=1500000.0



	N1=(A1-B1)/(A1+B1) # n
	N2=N1*N1
	N3=N2*N1 # n², n³
	E2=((A1*A1)-(B1*B1))/(A1*A1) # e²





	SINK=sin(K)
	COSK=cos(K)
	TANK=SINK/COSK
	TANK2=TANK*TANK
	COSK2=COSK*COSK
	COSK3=COSK2*COSK
	K3=K-K0
	K4=K+K0

	#ArcofMeridian
	J3=K3*(1+N1+1.25*(N2+N3))
	J4=sin(K3)*cos(K4)*(3*(N1+N2+0.875*N3))
	J5=sin(2*K3)*cos(2*K4)*(1.875*(N2+N3))
	J6=sin(3*K3)*cos(3*K4)*35/24*N3
	M=(J3-J4+J5-J6)*B1

  #VRH2
	Temp=1-E2*SINK*SINK
	V=A1/sqrt(Temp)
	R=V*(1-E2)/Temp
	H2=V/R-1.0

	P=L-L0
	P2=P*P
	P4=P2*P2
	J3=M+N0
	J4=V/2*SINK*COSK
	J5=V/24*SINK*(COSK3)*(5-(TANK2)+9*H2)
	J6=V/720*SINK*COSK3*COSK2*(61-58*(TANK2)+TANK2*TANK2)
	North=J3+P2*J4+P4*J5+P4*P2*J6
	J7=V*COSK
	J8=V/6*COSK3*(V/R-TANK2)
	J9=V/120*COSK3*COSK2
	J9=J9*(5-18*TANK2+TANK2*TANK2+14*H2-58*TANK2*H2)
	East=E0+P*J7+P2*P*J8+P4*P*J9

	print "N %.2f E %.2f" % (North, East)


print """
Mantorp, hitta.se
RT90:
X: 6472064, Y: 1469558
WGS84:
Lat N 58° 22′ 14″ Lon E 15° 17′ 5″
Decimal:
58.3708, 15.2850
"""

convert(58.3708,15.2850)
convert((58, 22, 14), (15, 17, 5))



print """

Sergelpinnen, eniro.se
WGS 84:N 59° 19.954', E 18° 3.910'
WGS 84 - decimal:59.33257, 18.06516
RT90: 6581267, 1628625
SWEREF99: 6581098, 674360
"""

convert(59.33256, 18.06516)
convert((59, 19.954, 0), (18, 3.910, 0))
