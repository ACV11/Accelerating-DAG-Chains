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

for i in range(20000,100000,20000):
	t = noclass_3_parallel.CreateNewGraphStructureObject(nodeArrivalSpeed=20)
	t1 = NewGraphStructure(nodeArrivalSpeed=10)
	print("number of transactions: ",2*i)
	l = []
	l.append(2*i)
	total_time = 1
	for k in range(10)
		for j in range(i):
			noclass_3_parallel.GetNextNode(t)
		time1 = noclass_3_parallel.globaltime
		total_time*=sum(time1)
		t = None
		t1 = None
		time1 = None
		noclass_3_parallel.globaltime = []
		noclass_3_parallel.graphPlot = networkx.OrderedDiGraph()
	l.append(total_time**(1/10))
	rows.append(l)



# name of csv file 
filename = "timing_records_parallel.csv"
  
# writing to csv file 
with open(filename, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
      
    # writing the fields 
    csvwriter.writerow(fields) 
      
    # writing the data rows 
    csvwriter.writerows(rows)
