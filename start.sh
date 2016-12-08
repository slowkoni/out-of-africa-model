#!/bin/bash

trap "echo trapped signal caught" HUP INT QUIT TERM

id
cd /home/popsim
./msprime-out-of-africa-3-pops.py $@
