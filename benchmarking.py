import numpy as np
import matplotlib.pyplot as plt
from code import NewGraphStructure
import time

plt.rc('axes', labelsize=20)
plt.rc('xtick', labelsize=20)
plt.rc('ytick', labelsize=20)

time_list = []
node_count = []

t = NewGraphStructure(nodeArrivalSpeed=25)

'''
for i in range(100,10000,100):
	node_count.append(i)
	start = time.time()
	for j in range(i):
		t.GetNextNode()
	end = time.time()
	print("===============================")
	print(i)
	print("time",end-start)
	time_list.append(end-start)
'''
start = time.time()
for j in range(100):
	print(j)
	t.GetNextNode()
end = time.time()
print("time is: ",end-start)
'''
plt.plot(node_count,time_list)
plt.show()
'''

