import numpy
import networkx
import matplotlib
import numba
from numba import njit
import numpy as np
import matplotlib.pyplot as plt
import time
import pymp

timer = []
time_update = []

class NewTrans(object):
	
	def  __init__(self, GraphStructure, currentTime, ListOfTip, Id):
		self.graph = GraphStructure
		self.createdAtTime = currentTime
		self.verifiedNodes = ListOfTip
		self.verifiedbyadjacent = set()
		self.verifiedby = set()
		self.timestamp = float('inf')
		self.Id = Id
		self.graph.graphPlot.add_node(self.Id,pos=(self.createdAtTime,numpy.random.uniform(-1,1)))
	
	def available(self) :
		if self.graph.currentTime >= self.createdAtTime + 1.0 :
			return True
		return False

	def tip(self) :
		#if self.graph.currentTime < self.timestamp :
		if self.timestamp == float('inf') :
			return True
		return False

	def tipDel(self):
		return self.graph.currentTime - 1.0 < self.timestamp

	def nodeWeight(self):
		weight = 1 + len(self.approved_by())
		self.tangle.trans = set()
		return weight

	def nodeWeightDel(self):
		weight = self.graph.weights.get(self.Id)
		if weight: 
			return weight
		else:
			weight = 1 + len(self.approved_by_delayed())
			self.graph.trans = set()
			self.graph.weights[self.Id] = weight
		return weight

	def approved_by(self):
		for node in self.verifiedbyadjacent:
		    if node not in self.graph.trans:
		        self.graph.trans.add(node)
		        self.graph.trans.update(node.approved_by())
		return self.graph.trans

	def approved_by_delayed(self):
		for node in self.approved_directly_by():
		    if node not in self.graph.trans:
		        self.graph.trans.add(node)
		        self.graph.trans.update(node.approved_by_delayed())
		return self.graph.trans

	def approved_directly_by(self):
	    return [node for node in self.verifiedbyadjacent if node.available()]

def delayTime(arrivalrate):
	return numpy.random.exponential(scale = 1.0/arrivalrate)

def lnu(noOfNodes,nodeArrivalSpeed):
	l = int(numpy.maximum(0, noOfNodes - 20.0*nodeArrivalSpeed))
	u = int(numpy.maximum(1, noOfNodes - 10.0*nodeArrivalSpeed))
	return (l,u)

def prob(alpha,nodeweight,wtlist):
	deno = numpy.sum(numpy.exp(-alpha * (nodeweight - wtlist)))
	#print("deno is: ",deno)
	probs = numpy.divide(numpy.exp(-alpha * (nodeweight - wtlist)),deno)
	return probs

class NewGraphStructure(object):

	def __init__(self, nodeArrivalSpeed=10, parameterAlpha=0.001):
		self.noOfNodes = 0
		self.currentTime = 1.0
		self.nodeArrivalSpeed = nodeArrivalSpeed
		self.parameterAlpha  = parameterAlpha
		self.graphPlot  = networkx.OrderedDiGraph()
		self.firstNode = StartNode(self)
		self.NodeList = []
		self.NodeList.append(self.firstNode)
		self.noOfNodes += 1
		self.weights = {}
		self.trans = set()
		self.traversalpath = []

	def FindMin(self,x,y):
		if x<y :
			return x
		else :
			return y

	def GetNextNode(self):
		# Get Next Transaction rate of arrival is a possion point process
		#print("Does print work??")
		DelayTime = delayTime(self.nodeArrivalSpeed)
		self.currentTime = self.currentTime + DelayTime
		# Get Available Tips from the Graph Using Weighted Random Walk
		ListOfTip = set(self.MontyCarloMarkovChain())
		#print(ListOfTip)
		NewNode = NewTrans(self,self.currentTime,ListOfTip,self.noOfNodes)
		self.noOfNodes = self.noOfNodes + 1
		#print(NewNode.Id)
		for node in ListOfTip :
			#print(node.Id)
			node.timestamp = self.FindMin(self.currentTime,node.timestamp)
			node.verifiedbyadjacent.add(NewNode)
			self.graphPlot.add_edges_from([(NewNode.Id,node.Id)])
		self.NodeList.append(NewNode)
		self.weights = {}

	def tips(self):
		ret = []
		for node in self.NodeList :
			if node.available() and node.tipDel() :
				ret.append(node)	
		return ret


	def MontyCarloMarkovChain(self):
		numWalkers = 6
		'''
		l = int(numpy.maximum(0, self.noOfNodes - 20.0*self.nodeArrivalSpeed))#didnt get this
		u = int(numpy.maximum(1, self.noOfNodes - 10.0*self.nodeArrivalSpeed))#or this
		'''
		x = lnu(self.noOfNodes,self.nodeArrivalSpeed)
		l = x[0]
		u = x[1]
		Nodes = self.NodeList[l:u]
		particles = numpy.random.choice(Nodes, numWalkers)
		start = time.time()
		for node in particles:
			self.RandomWeightedWalk(node)
		end = time.time()
		time_update.append(end-start)
		unapprovedtransactions = self.traversalpath[:2]
		self.traversalpath = []
		return unapprovedtransactions


	def RandomWeightedWalk(self, startnode):
		node = startnode
		while not node.tipDel() and node.available():
			if len(self.traversalpath) >= 2:
				return

			nextsetofnodes = node.approved_directly_by()
			if self.parameterAlpha > 0:
				#start1 = time.time()
				nodeweight = node.nodeWeightDel()
				#end1 = time.time()
				#time.append(end1 - start1)
				weightlist = numpy.array([])
				for i in nextsetofnodes:
					#start2 = time.time()
					x = i.nodeWeightDel()
					#end2 = time.time()
					#time.append(end2-start2)
					weightlist = numpy.append(weightlist, x)
				probs = prob(self.parameterAlpha,nodeweight,weightlist)
			else:
				probs = None
			node = numpy.random.choice(nextsetofnodes, p=probs)
		self.traversalpath.append(node)
 
	def plotgrp(self):
		pos = networkx.get_node_attributes(self.graphPlot, 'pos')
		networkx.draw_networkx_nodes(self.graphPlot, pos)
		networkx.draw_networkx_labels(self.graphPlot, pos)
		networkx.draw_networkx_edges(self.graphPlot, pos, edgelist=self.graphPlot.edges(), arrows=True)
		matplotlib.pyplot.xlabel('Time')
		matplotlib.pyplot.yticks([])
		matplotlib.pyplot.show()

class StartNode(NewTrans):
	def __init__(self, GraphStructure):
		#print(type(GraphStructure))
		self.graph = GraphStructure
		self.createdAtTime = 0
		self.verifiedNodes = []
		self.verifiedbyadjacent = set()
		self.timestamp = float('inf')
		self.Id = 0
		self.graph.graphPlot.add_node(self.Id,pos=(self.createdAtTime,0))
