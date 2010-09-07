#!/usr/bin/env python

import json

f=open("4000.txt")

data = json.load(f)

print len(data)
