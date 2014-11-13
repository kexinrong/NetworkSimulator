import simpy
import time

from output import RealTimeGraph
from input import input
from host import Host
from link import Link
from flow import Flow, SendingFlow

class MainEnv(simpy.Environment):
    """ The class for main environment for our network sumulator."""
    HOST_FIELDS = ['host_send_rate',
                   'host_receive_rate',
                  ]

    FLOW_FIELDS = ['flow_send_rate',
                   'flow_receive_rate',
                   'flow_avg_RTT',
                  ]

    LINK_FIELDS = ['packet_loss',
                   'buffer_occupancy',
                   'link_rate',
                  ]

    def __init__(self, duration, interval):
        """
            Args:
                duration:
                    user specified duration of simulation (in ms)
                interval:
                    interval that env collects data at (in ms)

            Attrs:
                hosts:
                    a list of host objs
                flows:
                    a list of flow objs
                routers:
                    a list of router objs
                links:
                    a list of link objs
                duration:
                    user specified duration of simulation (in ms)
                interval:
                    interval that env collects data at (in ms)
                realTimeGraph:
                    realTimeGraph obj
                maxId:
                    the max ID the network has assgined to any objs
        """
        super(MainEnv, self).__init__()
        self.hosts = []
        self.flows = []
        self.routers = []
        self.links = []
        self.duration = duration
        self.interval = interval
        self.realTimeGraph = None
        self.maxId = -1

    def newId(self):
        self.maxId += 1
        return self.maxId

    def loadNetwork(self, ifile):
        """ Sets up the network topology and objects.

            Args:
                input:
                    string; input file name;
        """

        network_specs = input(ifile)

        self.realTimeGraph = RealTimeGraph(self.duration,
                                           self.interval,
                                           network_specs['Hosts'],
                                           len(network_specs['Links']),
                                           len(network_specs['Flows']))

        for _ in range(network_specs['Hosts']):
            self.hosts.append(Host(self, self.newId()))

        # placeholder for creating routers

        for rate, delay, buffer_size, node1, node2 in network_specs['Links']:
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
            link = Link(self, self.newId(), rate, delay, buffer_size, endpoints)

            # add link to the nodes
            for node in endpoints:
                node.add_link(link)

            self.links.append(link)

        for data_amt, flow_start, src, dest in network_specs['Flows']:
            src -= 1
            dest -= 1

            src_host = self.hosts[src]
            dest_host = self.hosts[dest]
            sending_flow = SendingFlow(self, self.newId(), data_amt, flow_start,
                                       dest_host.get_id(), src_host)
            self.flows.append(sending_flow)
            src_host.add_flow(sending_flow)

    def collectData(self):
        """ Collects data from all the objects in the network. """
        new_data = {}
        fields = MainEnv.HOST_FIELDS + MainEnv.FLOW_FIELDS + MainEnv.LINK_FIELDS
        for field in fields:
            new_data[field] = []

        for host in self.hosts:
            host_data = host.report()
            for field in MainEnv.HOST_FIELDS:
                new_data[field] += [host_data[field]]

        for flow in self.flows:
            flow_data = flow.report()
            for field in MainEnv.FLOW_FIELDS:
                new_data[field] += [flow_data[field]]

        #for router in self.routers:
            # placeholder for routers

        for link in self.links:
            link_data = link.report()
            for field in MainEnv.LINK_FIELDS:
                new_data[field] += [link_data[field]]

        self.realTimeGraph.add_data_points(new_data)

    def start(self, ifile):
        """ Start our simulation.

            Args:
                input:
                    Input file for network topology and stats
        """

        self.loadNetwork(ifile)
        #self.realTimeGraph.plot()

        while self.now < self.duration:
            break_time = min(self.now + self.interval,
                             self.duration)
            self.run()
            self.collectData()
            time.sleep(0.1)
        
        self.realTimeGraph.export_to_jpg()
        self.realTimeGraph.export_to_file()

