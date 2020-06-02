'''
Code to paralleise the IOTA DAG. Look into the random weighted walk and mcmc function for further details.
Project by Ashish Christopher Victor, AKhilarkha Jayanthi and Atul Anand Gopalakrishnan
'''


import numpy
import networkx
import matplotlib
import numba
from numba import njit
import numpy as np
import matplotlib.pyplot as plt
import time
import pymp


# NewTrans Objects
graphPlot = networkx.OrderedDiGraph()
#sharedtraversalpath = pymp.shared.list()s
shared_rec = []
time_rec = 0
#rectime = pymp.shared.list()
count = 0

import os


def CreateNewTransObject(GraphStructure, currentTime, ListOfTip, Id) :
    NewTrans = dict()
    #NewTrans["graph"] = GraphStructure
    NewTrans["createdAtTime"] = currentTime
    NewTrans["verifiedNodes"] = ListOfTip
    NewTrans["verifiedbyadjacent"] = []
    NewTrans["verifiedby"] = set()
    NewTrans["timestamp"] = float('inf')
    NewTrans["Id"] = Id
    graphPlot.add_node(Id,pos=(currentTime,numpy.random.uniform(-1,1)))
    return NewTrans

def available(NewGraphStructure,NewTransObject) :
    if NewGraphStructure["currentTime"] >= NewTransObject["createdAtTime"] + 1.0 :
    	return True
    return False

def tipDel(NewGraphStructure,NewTransObject):
	#print("timestap_tipdel : ",NewTransObject["timestamp"])
	return NewGraphStructure["currentTime"] - 3.0 < NewTransObject["timestamp"]

w = pymp.shared.dict()
def nodeWeightDel(p,NewGraphStructure,NewTransObject):
	global shared_rec
	#start_rec = time.time()
	#weight = NewGraphStructure["weights"].get(NewTransObject["Id"])
	weight = None
	with p.lock:
		weight = w.get(NewTransObject["Id"])
	#print("Weight is: ",weight)
	if weight:
		global count
		count += 1
		return weight
	else:
		weight = 1 + len(approved_by_delayed(NewGraphStructure,NewTransObject["Id"]))
		NewGraphStructure["trans"] = set()
		#NewGraphStructure["weights"][NewTransObject["Id"]] = weight
		with p.lock:
			w[NewTransObject["Id"]] = weight
		#end_rec = time.time()
		#shared_rec.append(end_rec-start_rec)
	return weight

def approved_by_delayed(NewGraphStructure,NewTransObject):
    for Id in approved_directly_by(NewGraphStructure,NewGraphStructure["NodeList"][NewTransObject]):#NewGraphStructure["NodeList"][Id]=>Node
        if Id not in NewGraphStructure["trans"]:
            NewGraphStructure["trans"].add(Id)
            temp = approved_by_delayed(NewGraphStructure,Id)
            NewGraphStructure["trans"].update(temp)
    return NewGraphStructure["trans"]

def approved_directly_by(NewGraphStructure,NewTransObject):
	a = [node["Id"] for node in NewTransObject["verifiedbyadjacent"] if available(NewGraphStructure,node)]
	b = [node["Id"] for node in NewTransObject["verifiedbyadjacent"]]
	#print("directly : ",b)
	return a

def CreateNewGraphStructureObject(nodeArrivalSpeed=10, parameterAlpha=0.001):
    NewGraphStructure = dict()
    NewGraphStructure["noOfNodes"] = 0
    NewGraphStructure["currentTime"] = 1.0
    NewGraphStructure["nodeArrivalSpeed"] = nodeArrivalSpeed
    NewGraphStructure["parameterAlpha"]  = parameterAlpha
    #NewGraphStructure["graphPlot"]  = networkx.OrderedDiGraph()
    NewGraphStructure["NodeList"] = []
    NewGraphStructure["noOfNodes"] += 1
    NewGraphStructure["weights"] = {}
    NewGraphStructure["trans"] = set()
    NewGraphStructure["traversalpath"] = []
    NewGraphStructure["firstNode"] = CreateNewTransObject(NewGraphStructure,0, [], 0)
    NewGraphStructure["NodeList"].append(NewGraphStructure["firstNode"])
    #sharedtraversalpath.append(NewGraphStructure["firstNode"])
    return NewGraphStructure

def FindMin(x,y):
	if x<y :
		return x
	else :
		return y


def GetNextNode(NewGraphStructure):
	DelayTime = numpy.random.exponential(scale = 1.0/NewGraphStructure["nodeArrivalSpeed"],size = None)
	NewGraphStructure["currentTime"] = NewGraphStructure["currentTime"] + DelayTime
	ListOfTip = MontyCarloMarkovChain(NewGraphStructure)
	NewNode = CreateNewTransObject(NewGraphStructure,NewGraphStructure["currentTime"],ListOfTip,NewGraphStructure["noOfNodes"])
	NewNode2 = CreateNewTransObject(NewGraphStructure,NewGraphStructure["currentTime"],ListOfTip,NewGraphStructure["noOfNodes"]+1)

	#print("new : ",NewNode["Id"])
	NewGraphStructure["noOfNodes"] = NewGraphStructure["noOfNodes"] + 1
	for node in ListOfTip[:2] :
		#print("node id : ",node["Id"])
		node["timestamp"] = FindMin(NewGraphStructure["currentTime"],node["timestamp"])
		NewGraphStructure["NodeList"][node["Id"]] = node
		#print("timestamp_get_next_node: ",node["timestamp"])
		node["verifiedbyadjacent"].append(NewNode)
		graphPlot.add_edges_from([(NewNode["Id"],node["Id"])])
	NewGraphStructure["noOfNodes"] = NewGraphStructure["noOfNodes"] + 1
	if(len(ListOfTip)>2) :
		ListOfTip.pop()
	if(len(ListOfTip)>2) :
		ListOfTip.pop()
	for node in ListOfTip[:2] :
		#print("node id : ",node["Id"])
		node["timestamp"] = FindMin(NewGraphStructure["currentTime"],node["timestamp"])
		NewGraphStructure["NodeList"][node["Id"]] = node
		#print("timestamp_get_next_node: ",node["timestamp"])
		node["verifiedbyadjacent"].append(NewNode2)
		graphPlot.add_edges_from([(NewNode2["Id"],node["Id"])])

	NewGraphStructure["NodeList"].append(NewNode)
	NewGraphStructure["NodeList"].append(NewNode2)

	#NewGraphStructure["weights"] = {}
	w = pymp.shared.dict()

def tips(NewGraphStructure):
	ret = []
	for node in NewGraphStructure["NodeList"] :
		if available(NewGraphStructure,node) and tipDel(NewGraphStructure,node) :
			ret.append(node)
	return ret


globaltime = []
globaltime2 = []

'''
The function helps us select a bunch of unapproved nodes and the incoming transcation can approve that. This is paralleised using pymp on 4 threads.
'''
def MontyCarloMarkovChain(NewGraphStructure):
	numWalkers = 4
	unnaproved = []

	l = int(numpy.maximum(0, NewGraphStructure["noOfNodes"] - 20.0*NewGraphStructure["nodeArrivalSpeed"]))
	u = int(numpy.maximum(1, NewGraphStructure["noOfNodes"] - 10.0*NewGraphStructure["nodeArrivalSpeed"]))
	Nodes = NewGraphStructure["NodeList"][l:u]
	particles = numpy.random.choice(Nodes, min(numWalkers, len(Nodes)), replace=False)
	rng = len(particles)
	time_shared = pymp.shared.list()
	
	#st = time.time()
	with pymp.Parallel(4) as p :
		#sharedtraversalpath_1 = []
		start = time.time()
		for node in p.range(0,rng):
			onenode = RandomWeightedWalk(p,NewGraphStructure,particles[node])
			with p.lock :
				unnaproved.append(onenode)
		end = time.time()
		#print(end-start)
		with p.lock :
			time_shared.append(end-start)
		#l = random.choice(sharedtraversalpath,k=2)
	#et = time.time()
	#print(et-st)
	global globaltime
	#print(time_shared)
	globaltime.append(max(time_shared))
	return unnaproved

'''
Helps backtrack and identify nodes that are unapproved.
'''

def RandomWeightedWalk(p,NewGraphStructure, startnode):
	node = startnode
	
	#global sharedtraversalpath
	global shared_rec#r
	global rectime#r
	global time_rec#r
	#print("startnode",startnode,end="\n\n\n")
	#print(not tipDel(NewGraphStructure,node),available(NewGraphStructure,node))
	while not tipDel(NewGraphStructure,node) and available(NewGraphStructure,node):
		nextsetofnodes = approved_directly_by(NewGraphStructure,node)#Id for next set of nodes		
		#print(nextsetofnodes)
		for number in range(len(nextsetofnodes)) :
			nextsetofnodes[number] = NewGraphStructure["NodeList"][nextsetofnodes[number]]
		if NewGraphStructure["parameterAlpha"] > 0:
			nodeweight = nodeWeightDel(p,NewGraphStructure,node)
			weightlist = numpy.array([])
			
			for i in nextsetofnodes:
				weightlist = numpy.append(weightlist, nodeWeightDel(p,NewGraphStructure,i))
			#print("cal prob")
			#shared_rec.append(end_rec-start_rec)
			deno = numpy.sum(numpy.exp(-NewGraphStructure["parameterAlpha"] * (nodeweight - weightlist)))
			probs = numpy.divide(numpy.exp(-NewGraphStructure["parameterAlpha"] * (nodeweight - weightlist)), deno)
		else:
			probs = None
		node = numpy.random.choice(nextsetofnodes, p=probs)
	#print("node : ", node["Id"])
	return node	

def plotgrp(NewGraphStructure):
	pos = networkx.get_node_attributes(graphPlot, 'pos')
	networkx.draw_networkx_nodes(graphPlot, pos)
	networkx.draw_networkx_labels(graphPlot, pos)
	networkx.draw_networkx_edges(graphPlot, pos, edgelist=graphPlot.edges(), arrows=True)
	matplotlib.pyplot.xlabel('Time')
	matplotlib.pyplot.yticks([])
	matplotlib.pyplot.show()
