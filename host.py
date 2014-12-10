"""Defines the properties and methods of network host processes."""

from packet import Packet, RoutingUpdatePacket
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
    """
    
    MBPS_TO_B_PER_MS = 131.072

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
        
        # Amount of data sent and received in bytes to report average per-host
        # send/receive rate in Mbps.
        self.amt_data_sent = 0.0
        self.amt_data_received = 0.0

        # Set up host monitoring of outgoing and incoming packets.
        env.process(self.monitor_outgoing_packets(self.env))
        env.process(self.monitor_incoming_packets(self.env))
        
    def get_id(self):
        """Returns host ID."""
        return self.host_id
    
    def get_link_rate(self):
        """Returns the transmission rate of the outbound link."""
        if (self.link == None):
            return 0.0
        else:
            return self.link.get_link_rate()
        
    def get_num_flows(self):
        """Returns the number of flows residing in this host."""
        return len(self.flows)
    
    def get_buffer_size(self):
        """Returns the buffer size of the outbound link in bytes."""
        if (self.link == None):
            return 0.0
        else:
            return self.link.get_buffer_size()
    
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
            Host passivates until an internal flow calls send_packet. It then
            places all outgoing packets into the link buffer for transmission.
            No collision control is implemented.
        """
        
        while True:
            # Passivate until a flow wants to send a packet.
            yield self.send_packet_event
            
            # Place outgoing packets in link buffer.
            for outgoing_packet in self.outgoing_packets:
                self.amt_data_sent += outgoing_packet.get_length()
                self.link.enqueue(outgoing_packet, self.get_id())
                
            # Empty outgoing_packets buffer and reset notification event.
            self.outgoing_packets = []
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

            # Assuming one link per host, no collisions can occur and
            # incoming_packets buffer necessarily has only one packet in it.
            incoming_packet = self.incoming_packets.pop()
            self.amt_data_received += incoming_packet.get_length()
            flow_id = incoming_packet.get_flow_id()

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
        # Add packet to outgoing_packet buffer.
        self.outgoing_packets.append(outgoing_packet)

        # Reactivate host unless collision has occured.
        if not self.send_packet_event.triggered:
            self.send_packet_event.succeed()

    def receive_packet(self, incoming_packet):
        """Method called by link to transmit packet into the host."""
        if (incoming_packet.get_packet_type() !=
            Packet.PacketTypes.routing_update_packet):
            
            # Add packet to incoming_packet buffer.
            self.incoming_packets.append(incoming_packet)

            # Reactivate host. No possibility of collision, but check in case.
            if not self.receive_packet_event.triggered:
                self.receive_packet_event.succeed()

    def report(self):
        """Report the average per-host send/receive rate in units of Mbps since
        the last time this function was called."""
        
        # We report send/receive rates in units of Mbps by dividing amount of
        # data sent/received in kB by the time interval in ms.
        B_TO_KB = 1000
        
        # Rate of packets sent from this host.
        host_send_rate = self.amt_data_sent / \
            (self.env.interval * Host.MBPS_TO_B_PER_MS)
        
        # Rate of packets received by this host.
        host_receive_rate = self.amt_data_received / \
            (self.env.interval * Host.MBPS_TO_B_PER_MS)
        
        # Reset measurements.
        self.amt_data_sent = 0.0
        self.amt_data_received = 0.0
        
        return {'host_send_rate' : host_send_rate,
                'host_receive_rate' : host_receive_rate}
