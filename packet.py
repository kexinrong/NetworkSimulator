"""Base class for network packets.

Subclasses derived from this base class include DataPacket,
AcknowledgementPacket, RoutingUpdatePacket, and FINPacket.
"""

class Packet(object):
    """
        Defines the properties and methods of general network packets.
    
        Attributes:
                PacketTypes:
                    An enum indicating the type of packet ('data packet',
                    'acknowledgement_packet', 'routing_update_packet', or
                    'fin_packet').
    """
    
    class PacketTypes(object):
        """
        An enum indicating the type of packet ('data packet',
        'acknowledgement_packet', 'routing_update_packet', or 'fin_packet').
        """
        
        data_packet = 1
        ack_packet = 2
        routing_update_packet = 3
        fin_packet = 4
    
    def __init__(
        self, src, flow_id, dest, timestamp, length, packet_type,seq_num):
        """
            Sets up a network packet with the given specifications:
        
            Args:
                    src:
                        Source address.
                    flow_id:
                        Sending/receiving flow ID.
                    dest:
                        Destination address.
                    timestamp:
                        Time upon sending packet.
                    length:
                        Length of the packet in bytes.        
                    packet_type:
                        An enum indicating the type of packet ('data packet',
                        'acknowledgement_packet', 'routing_update_packet', or
                        'fin_packet').
                    seq_num:
                        Packet sequence number in a given flow.
        """
        
        self.src = src
        self.flow_id = flow_id
        self.dest = dest
        self.timestamp = timestamp
        self.length = length
        self.packet_type = packet_type
        self.seq_num = seq_num
        
    def get_source(self):
        """Returns source address."""
        return self.src
    
    def get_flow_id(self):
        """Returns sending/receiving flow ID."""
        return self.flow_id
    
    def get_destination(self):
        """Returns destination address."""
        return self.dest
    
    def get_timestamp(self):
        """Returns the timestamp."""
        return self.timestamp
    
    def get_length(self):
        """Returns the packet length."""
        return self.length
    
    def get_packet_type(self):
        """Returns the packet type."""
        return self.packet_type

    def packet_type_str(self):
        if self.packet_type == Packet.PacketTypes.data_packet:
            return "data"
        elif self.packet_type == Packet.PacketTypes.ack_packet:
            return "ack"
        elif self.packet_type == Packet.PacketTypes.routing_update_packet:
            return "routing"
        else:
            return "fin"
    
    def get_seq_num(self):
        """Returns the packet's sequence number relative to a flow."""
        return self.seq_num

    def set_source(self, src):
        """Sets source address."""
        self.src = src
    
    def set_destination(self, dest):
        """Sets destination address."""
        self.dest = dest
        
    def set_timestamp(self, timestamp):
        """Updates timestamp of packet."""
        self.timestamp = timestamp
    
    def set_seq_num(self, seq_num):
        """Sets the packet's sequence number relative to a flow."""
        self.seq_num = seq_num
        
class DataPacket(Packet):
    """
        Defines the properties and methods of a data packet.

        For the purposes of this simulation, a data packet need not actually
        contain a payload. The size of a data packet is fixed at 1024 bytes.
    """
    
    DATA_PACKET_LENGTH = 1024
    
    def __init__(self, src, flow_id, dest, timestamp, seq_num):
        """
            Sets up a data packet with the given specifications:
                
            Args:
                    src:
                        Source address.
                    flow_id:
                        Sending/receiving flow ID.
                    dest:
                        Destination address.
                    timestamp:
                        Time upon sending packet.
                    seq_num:
                        Packet sequence number in a given flow.
            
            The packet_type attribute is set to 'data_packet'.
        """
        
        super(DataPacket, self).__init__(src, flow_id, dest, timestamp,
            self.DATA_PACKET_LENGTH, Packet.PacketTypes.data_packet, seq_num)

class AckPacket(Packet):
    """
        Defines the properties and methods of an acknowledgement packet.
    
        An acknowledgment packet will acknowledge a particular data packet
        through its seq_num attribute. Acknowledgment packets have a fixed
        size of 64 bytes.
    """
    
    ACKNOWLEDGMENT_PACKET_LENGTH = 64
    
    def __init__(self, src, flow_id, dest, timestamp, seq_num):
        """
            Sets up an acknowledgement packet with the given specifications:
                
            Args:
                    src:
                        Source address.
                    flow_id:
                        Sending/receiving flow ID.
                    dest:
                        Destination address.
                    timestamp:
                        Time upon sending packet.
                    seq_num:
                        Packet sequence number in a given flow.
            
            The packet_type attribute is set to 'acknowledgement_packet'.
        """
        
        super(AckPacket, self).__init__(src, flow_id, dest, timestamp,
            self.ACKNOWLEDGMENT_PACKET_LENGTH,
            Packet.PacketTypes.ack_packet, seq_num)
        
class RoutingUpdatePacket(Packet):
    """
        Defines the properties and methods of a routing update packet.
    
        Routers implement dynamic routing through the Bellman-Ford algorithm.
        Thus, a routing update packet will contain a table of distance estimates
        to each router. Routing update packets have a fixed size of 1024 bytes.
    """
    
    ROUTING_UPDATE_PACKET_LENGTH = 1024
    
    def __init__(self, src, flow_id, dest, timestamp, seq_num, dist_estimates):
        """
            Sets up a routing update packet with the given specifications:
                
            Args:
                    src:
                        Source address.
                    flow_id:
                        Sending/receiving flow ID.
                    dest:
                        Destination address.
                    timestamp:
                        Time upon sending packet.
                    seq_num:
                        Packet sequence number in a given flow.
                    dist_estimates:
                        Table of distance estimates to each router as a dict of
                        costs {destination_id: cost}.
            
            The packet_type attribute is set to 'routing_update_packet'.
        """
        
        super(RoutingUpdatePacket, self).__init__(
            src, flow_id, dest, timestamp, self.ROUTING_UPDATE_PACKET_LENGTH,
            Packet.PacketTypes.routing_update_packet, seq_num)
        
        self.dist_estimates = dist_estimates
        
    def get_distance_estimates(self):
        """Returns the table of distance estimates computed by the source router
        at the given timestamp."""
        return self.dist_estimates

class FINPacket(Packet):
    """
        Defines the properties and methods of an FIN packet.
    
        A FIN packet signals the termination of a TCP connection. Like
        acknowledgment packets, FIN packets have a fixed size of 64 bytes.
    """
    
    FIN_PACKET_LENGTH = 64
    
    def __init__(self, src, flow_id, dest, timestamp, seq_num):
        """
            Sets up a data packet with the given specifications:
                
            Args:
                    src:
                        Source address.
                    flow_id:
                        Sending/receiving flow ID.
                    dest:
                        Destination address.
                    timestamp:
                        Time upon sending packet.
                    seq_num:
                        Packet sequence number in a given flow.
            
            The packet_type attribute is set to 'fin_packet'.
        """
        
        super(FINPacket, self).__init__(src, flow_id, dest, timestamp,
            self.FIN_PACKET_LENGTH, Packet.PacketTypes.fin_packet, seq_num)
