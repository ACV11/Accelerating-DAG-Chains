import numpy
import networkx
import matplotlib


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
		DelayTime = numpy.random.exponential(scale = 1.0/self.nodeArrivalSpeed,size = None)
		self.currentTime = self.currentTime + DelayTime
		# Get Available Tips from the Graph Using Weighted Random Walk
		ListOfTip = set(self.MontyCarloMarkovChain())
		NewNode = NewTrans(self,self.currentTime,ListOfTip,self.noOfNodes)
		self.noOfNodes = self.noOfNodes + 1
		for node in ListOfTip :
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
		numWalkers = 10
		l = int(numpy.maximum(0, self.noOfNodes - 20.0*self.nodeArrivalSpeed))
		u = int(numpy.maximum(1, self.noOfNodes - 10.0*self.nodeArrivalSpeed))
		Nodes = self.NodeList[l:u]
		particles = numpy.random.choice(Nodes, numWalkers)
		for node in particles:
			self.RandomWeightedWalk(node)
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
				nodeweight = node.nodeWeightDel()
				weightlist = numpy.array([])
				for i in nextsetofnodes:
					weightlist = numpy.append(weightlist, i.nodeWeightDel())
				deno = numpy.sum(numpy.exp(-self.parameterAlpha * (nodeweight - weightlist)))
				probs = numpy.divide(numpy.exp(-self.parameterAlpha * (nodeweight - weightlist)), deno)
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
		self.graph = GraphStructure
		self.createdAtTime = 0
		self.verifiedNodes = []
		self.verifiedbyadjacent = set()
		self.timestamp = float('inf')
		self.Id = 0
		self.graph.graphPlot.add_node(self.Id,pos=(self.createdAtTime,0))




