import gps
import time
import json

def flattendw(dw):

  if isinstance(dw, gps.dictwrapper):
    return flattendw(dw.__dict__) #Break out the inner dict and try again

  if type(dw)==dict:
    d = {}
    for k in dw.keys():
      d[k] = flattendw(dw[k])
    return d

  if type(dw)==list:
    l = []
    for i in dw:
      l += [flattendw(i)]
    return l

  if type(dw)==tuple:
    t = ()
    for i in dw:
      t += (flattendw(i),)
    return t

  if type(dw) in (str, float, int):
    return dw

  #Someting unbeknownst to man
  return dw


session=gps.gps(mode=gps.WATCH_ENABLE|gps.WATCH_NEWSTYLE|gps.WATCH_JSON)

while True:
  dw = session.next()

  d = flattendw(dw)

  #print json.dumps(d, sort_keys=True, indent=2)
  print json.dumps(d)

  continue

  if d["class"]=="TPV":
    lon=d["lon"]
    lat=d["lat"]
    z  =d["alt"]
    t  =d["time"]
    v  =d["speed"]

    print "%s: %.7f %.7f %.1fm %.2fm/s" % (t, lon, lat, z, v)
