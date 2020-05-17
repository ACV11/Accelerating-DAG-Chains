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


fields = ['number_of_transactions','parallel_time']

rows = []

affinity_mask = {0, 1, 2, 3, 4, 5}
os.sched_setaffinity(os.getpid(), affinity_mask)

t = noclass_3_parallel.CreateNewGraphStructureObject(nodeArrivalSpeed=20)

for i in range(5000):
	#print(i)
	noclass_3_parallel.GetNextNode(t)

time1 = noclass_3_parallel.globaltime

print("Total time: ",sum(time1))
print("Avg time: ",sum(time1)/10000)

#noclass_3_parallel.plotgrp(t)
