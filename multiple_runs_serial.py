import numpy as np
import matplotlib.pyplot as plt
import noclass_3_parallel
import code1
from code1 import NewGraphStructure
import os
import csv
import networkx

plt.rc('axes', labelsize=20)
plt.rc('xtick', labelsize=20)
plt.rc('ytick', labelsize=20)

import time


#print("This process has the PID", os.getpid())

plt.figure(figsize=(25, 100))


fields = ['number_of_transactions','serial_time']

rows = []

affinity_mask = {0}
os.sched_setaffinity(os.getpid(), affinity_mask)

t = NewGraphStructure(nodeArrivalSpeed=20)
for i in range(10000):
	t.GetNextNode()

time1 = code1.time_update

#time1 = noclass_3_parallel.globaltime
#t.plotgrp()
print("Total time: ",sum(time1))
