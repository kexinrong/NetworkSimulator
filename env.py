import simpy
import time

class MainEnv(simpy.Environment):
	'''The class for main environment for our network sumulator.'''

	def __init__(self):
		super(MainEnv, self).__init__()
		self.hosts = []
		self.flows = []
		self.routers = []
		self.links = []
		self.data = {}
		self.output = ''
	
	def loadNetwork(self, input):
		'''Sets up the network topology and objects.
		'''
		# Will be implemented later when input is implemented
		pass

	def setOutput(self, output):
		'''Sets the output file'''
		self.output = output

	def handleHostData(self, hostData):
		'''Handles the data reported by a host.'''
		pass
	
	def handleFlowData(self, flowData):
		'''Handles the data reported by a flow.'''
		pass

	def handleRouterData(self, routerData):
		'''Handles the data reported by a router.'''
		pass

	def handleLinkData(self, linkData):
		'''Handles the data reported by a link.'''
		pass
	
	def displayData(self):
		'''Draws the graph of our data.'''
		pass 
	
	def outputData(self):
		'''Saves data to file.'''
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
		
		self.displayData()

	def start(self, total_duration, report_period, input, output):
		'''Start our simulation.

		Args:
			total_duration: int; 
				Total duration of our simulation
			report_period: int; 
				During each report_period, main_env will
				collect and display network statistics
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
		
		while self.now < total_duration:
			break_time = min(self.now + report_period, 
					 total_duration)
			self.run(until=break_time)
			self.collectData()
			time.sleep(0.1)
			
