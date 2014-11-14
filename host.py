"""Defines the properties and methods of network host processes."""

from flow import ReceivingFlow

class Host(object):
    """ 
        A host represents an endpoint device containing multiple sending and
        receiving flow connections.
    
        The host takes packets from its flows and feeds it into the link. A
        collision results in no sent packets, though the involved flows are
        notified. They can in turn follow a collision control protocol (e.g.,
        Aloha method).
    
        The host delivers incoming packets to the corresponding flows based on
        the flow_id parameter of the packet. It will dynamically generate a
        ReceivingFlow to handle new connections.
    
        Attributes:        
                PROCESSING_TIME:
                    Amount of time for host to respond to packet send
                    requests. Primarily for implementing collision detection.
    """

    PROCESSING_TIME = 0.0000000000000001

    def __init__(self, env, host_id, link=None, flows=None):
        """
            Sets up a network endpoint host object.
        
            Args:            
                    env:
                        SimPy environment in which host resides.
                    host_id:
                        Identification number of host.
                    link:
                        Link object connecting host to the internet. Optional
                        during initialization, defaults to None.
                    flows:
                        Dictionary of flows within host with flow IDs as keys.
                        Initially, this should only consist of sending flows
                        since receiving flows are generated on-the-fly. Optional
                        during initialization, defaults to empty dictionary.
                
            Attributes:
                    outgoing_packets:
                        Array of outgoing packets. Collision occurs when this
                        array has more than one packet.
                    incoming_packets:
                        Singleton array of packet received from internet. No
                        possibility of collision since only one link connecting
                        host to network.
                    send_packet_event:
                        Internal event triggered when flow wants to send packet.
                    receive_packet_event:
                        Internal event trigerred when packet arrives from
                        network.
        """
        
        self.env = env
        self.host_id = host_id
        self.link = link
        self.flows = flows
        
        # Set up packet buffers and notification events.
        self.outgoing_packets = []
        self.incoming_packets = []
        self.send_packet_event = env.event()
        self.receive_packet_event = env.event()
        
        # Counters to report average per-host send/receive rate.
        self.num_packets_sent = 0.0
        self.num_packets_received = 0.0

        # Set up host monitoring of outgoing and incoming packets.
        env.process(self.monitor_outgoing_packets(self.env))
        env.process(self.monitor_incoming_packets(self.env))
        
    def get_id(self):
        """Returns host ID."""
        return self.host_id
    
    def add_link(self, link):
        """Connect the host to a link, provided one does not already exist."""
        assert(self.link == None)
        self.link = link
    
    def add_flow(self, flow):
        """Insert a sending flow into the host."""
        if not self.flows:
            self.flows = {}
        self.flows[flow.get_id()] = flow    
        
    def remove_flow(self, flow_id):
        """Remove flow from host. It is a good convention for flows that have
        finished sending/receiving to remove themselves from the host."""
        del self.flows[flow_id]

    def monitor_outgoing_packets(self, env):
        """
            Host passivates until an internal flow calls send_packet. Upon
            reactivation, it waits for PROCESSING_TIME to gather all
            simultaneous outgoing packet requests. It sends a packet if only one
            request is issued, otherwise it notifies the corresponding hosts of
            a collision without sending any packets.
        """
        
        while True:
            # Passivate until a flow wants to send a packet.
            yield self.send_packet_event
            
            # Process outgoing packet requests from flows. Necessary for
            # collision detection.
            yield env.timeout(Host.PROCESSING_TIME)
            
            # Add packet into link buffer if no collisions have occured.
            if len(self.outgoing_packets) == 1:
                self.link.enqueue(self.outgoing_packets.pop(), self.get_id())
                self.num_packets_sent += 1
                
            # If collision occurs, notify appropriate flows which of their
            # packets collided without sending any packets.
            else:
                for packet in self.outgoing_packets:
                    flow = self.flows[packet.get_flow_id()]
                    flow.notify_collision(packet.get_seq_num())

                self.outgoing_packets = []

            # Reset outgoing packet notification event.
            self.send_packet_event = env.event()

    def monitor_incoming_packets(self, env):
        """
            Host passivates until link calls receive_packet. Upon reactivation,
            it attempts to forward the incoming packet to the corresponding
            flow. If a flow does not exist to handle the incoming packet, a
            receiving flow is generated on-the-fly.
        """

        while True:
            # Passivate until a packet arrives from the link.
            yield self.receive_packet_event
            self.num_packets_received += 1

            # Assuming one link per host, no collisions can occur and
            # incoming_packets buffer necessarily has only one packet in it.
            incoming_packet = self.incoming_packets.pop()
            flow_id = incoming_packet.get_flow_id()
            
            # Debug message.
            print "Host " + str(self.get_id()) + ": packet coming from" \
                  " Flow " + str(flow_id)
            # Immediately forward incoming packet to corresponding flow, if it
            # exists.
            if self.flows and flow_id in self.flows:
                self.flows[flow_id].receive_packet(incoming_packet)
            # Otherwise create a new receiving flow on-the-fly. 
            else:
                if not self.flows:
                    self.flows = {}
                new_receiving_flow = ReceivingFlow(env, flow_id,
                    incoming_packet.get_source(), self)
                self.flows[flow_id] = new_receiving_flow
                new_receiving_flow.receive_packet(incoming_packet)

            # Reset incoming packet notification event.
            self.receive_packet_event = env.event()            

    def send_packet(self, outgoing_packet):
        """Method called by internal flows to send packets into the network."""
        # Debug message
        print "Host " + str(self.get_id()) + " sending " + \
              outgoing_packet.packet_type_str() + " packet_" + \
              str(outgoing_packet.get_seq_num())
        # Add packet to outgoing_packet buffer.
        self.outgoing_packets.append(outgoing_packet)

        # Reactivate host unless collision has occured.
        if not self.send_packet_event.triggered:
            self.send_packet_event.succeed()

        
    def receive_packet(self, incoming_packet):
        """Method called by link to transmit packet into the host."""
        # Debug message
        print "Host " + str(self.get_id()) + " receiving " + \
            incoming_packet.packet_type_str() + " packet_" + \
            str(incoming_packet.get_seq_num()) 
        # Add packet to incoming_packet buffer.
        self.incoming_packets.append(incoming_packet)

        # Reactivate host. No possibility of collision, but check in case.
        if not self.receive_packet_event.triggered:
            self.receive_packet_event.succeed()        

    def report(self):
        """Report the average per-host send/receive rate in units of packets/s 
        since the last time this function was called."""
        
        time_interval_in_s = self.env.interval * 0.001
        
        # Rate of packets sent from this host.
        host_send_rate = self.num_packets_sent / time_interval_in_s
        
        # Rate of packets received by this host.
        host_receive_rate = self.num_packets_received / time_interval_in_s
        
        # Reset counters.
        self.num_packets_sent = 0.0
        self.num_packets_received = 0.0
        
        return {'host_send_rate' : host_send_rate,
                'host_receive_rate' : host_receive_rate}
