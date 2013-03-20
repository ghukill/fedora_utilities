#script for passing list of PID's as first argument

import os
from string import Template
import sys

#set variables
obj_pids = []

#read object list, push PIDs to list
object_list_file = sys.argv[1]
fhand = open(object_list_file,'r')

for line in fhand:
	pid = line.split('/')[1].strip()
	obj_pids.append(pid)