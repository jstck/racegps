#!/bin/bash

RUNS=100000

LOOPS=3

for i in $(seq ${LOOPS})
do

echo loop ${i}

echo "gps3.py:"
time ./gps3.py ${RUNS}

echo "convert.py:"
time ./convert.py ${RUNS}



done
