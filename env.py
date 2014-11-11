import simpy
import time

from output.py import *
from input_network import *
from host import *
from link import *
from flow import *

class MainEnv(simpy.Environment):
	'''The class for main environment for our network sumulator.'''
    HOST_FIELDS = ['host_send_rate',
                   'host_receive_rate',
                  ]
                    
    FLOW_FIELDS = ['flow_send_rate',
                   'flow_receive_rate,
                   'flow_avg_RTT',
                  ]
        
    LINK_FIELDS = ['packet_loss',
                   'buffer_occupancy',
                   'link_rate',
                  ]
	
    def __init__(self, duration, interval):
        '''
        Args:
            duration: user specified duration of simulation (in ms)
            interval: interval that env collects data at (in ms)
        '''
        super(MainEnv, self).__init__()
        self.hosts = []
        self.flows = []
        self.routers = []
        self.links = []
        self.duration = duration
        self.interval = interval
        self.realTimeGraph = RealTimeGraph(duration, interval)
        self.maxId = -1
	
    def newId(self):
        self.maxId += 1
        return self.maxId
    
    def loadNetwork(self, input):
        '''Sets up the network topology and objects.

        Args:
            input: string; input file name;
        '''
		
        network_specs = input_network(input)
		
        for _ in range(network_specs['Hosts']):
            self.hosts.append(Host(self, self.newId()))
        
        # placeholder for creating routers
        
        for rate, delay, buffer, node1, node2 in network_specs['Links']:
            # fetch endpoints
            endpoints = []
            # note this id here should start with 0
            for type, id in [node1, node2]:
                id -= 1
                if type == 'H':
                    endpoints.append(self.hosts[id])
                else:
                    endpoints.append(self.routers[id])
            
            # create link obj
            link = Link(self, self.newId(), rate, delay, buffer, endpoints)
            
            # add link to the nodes
            for node in endpoints:
                node.add_link(link)
            
            self.links.apend(link)
        
        for data_amt, flow_start, src, dest in network_specs['Flows']:
            src -= 1
            dest -= 1
            
            src_host = self.hosts[src]
            dest_host = self.hosts[dest]
            sending_flow = SendingFlow(self, self.newId(), data_amt, start,
                                       dest_host.get_id(), src_host)
            src_host.add_flow(sending_flow)
        
    def collectData(self):
		'''Collects data from all the objects in the network.'''
        new_data = {}
        for field in (HOST_FIELDS + FLOW_FIELDS + LINK_FIELDS):
            new_data[field] = []
    
		for host in self.hosts:
			host_data = host.report()
            for field in HOST_FIELDS:
                new_data[field] += [host_data[field]]

		for flow in self.flows:
			flow_data = flow.report()
            for field in FLOW_FIELDS:
                new_data[field] += [flow_data[field]]
        
		for router in self.routers:
			# placeholder for routers

		for link in self.links:
            link_data = link.report()
			for field in LINK_FIELDS:
                new_data[field] += [link_data[field]]
		
		self.realTimeGraph.add_data_points(new_data)
		self.realTimeGraph.animate()
		self.realTimeGraph.export_to_jpg()
		self.realTimeGraph.export_to_file()

	def start(self, input):
		'''Start our simulation.

		Args:
			input: 
				Input file for network topology and stats
			output:
				output file for network stats
		'''

		self.loadNetwork(input)
		
		while self.now < self.duration:
			break_time = min(self.now + self.interval, 
					 total_duration)
			self.run(until=break_time)
			self.collectData()
			self.realTimeGraph.plot()
			time.sleep(0.1)
			
