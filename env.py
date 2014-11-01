import simpy
import time
from output.py import *
from input_network import *

class MainEnv(simpy.Environment):
	'''The class for main environment for our network sumulator.'''
	
	def __init__(self, duration, interval):
		'''
		Args:
			duration: user specified duration of simulation (in sec)
			interval: interval that env collects data at (in sec)
		'''
		super(MainEnv, self).__init__()
		self.hosts = []
		self.flows = []
		self.routers = []
		self.links = []
		self.duration = duration
		self.interval = interval
		self.realTimeGraph = RealTimeGraph(duration, interval)
	
	def loadNetwork(self, input):
		'''Sets up the network topology and objects.

		Args:
			input: string; input file name;
		'''
		
		network_specs = input_network(input)
		
		# placeholder for creating these objects

	def handleHostData(self, hostData, new_data):
		'''Handles the data reported by a host.'''
		pass
	
	def handleFlowData(self, flowData, new_data):
		'''Handles the data reported by a flow.'''
		pass

	def handleRouterData(self, routerData, new_data):
		'''Handles the data reported by a router.'''
		pass

	def handleLinkData(self, linkData, new_data):
		'''Handles the data reported by a link.'''
		pass
	
	def collectData(self):
		'''Collects data from all the objects in the network.'''

		for host in self.hosts:
			self.handleHostData(host.report())
		for flow in self.flows:
			self.handleFlowData(flow.report())
		for router in self.routers:
			self.handleRouterData(router.report())
		for link in self.links:
			self.handleLinkData(link.report())
		
		self.realTimeGraph.add_data_points(self.data)
		self.realTimeGraph.animate()
		self.realTimeGraph.export_to_jpg()
		self.realTimeGraph.export_to_file()

	def start(self, input, output):
		'''Start our simulation.

		Args:
			input: 
				Input file for network topology and stats
			output:
				output file for network stats
		'''

		self.loadNetwork(input)
		self.setOutput(output)		

		# First start all our objects
		for host in self.hosts:
			self.process(host.start(env))
		for flow in self.flows:
			self.process(flow.start(env))
		for link in self.links:
			self.process(link.start(env))
		for router in self.routers:
			self.process(router.start(env))
		
		while self.now < self.duration:
			break_time = min(self.now + self.interval, 
					 total_duration)
			self.run(until=break_time)
			self.collectData()
			self.realTimeGraph.plot()
			time.sleep(0.1)
			
