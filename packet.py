"""Base class for network packets.

Subclasses derived from this base class include DataPacket,
AcknowledgementPacket, RoutingUpdatePacket, and FINPacket.
"""

from enum import Enum

class Packet(object):
    """Defines the properties and methods of general network packets.
    
    Attributes:
        PacketTypes: An enum indicating the type of packet ('data packet',
            'acknowledgement_packet', 'routing_update_packet', or 'fin_packet').
    """
    
    PacketTypes = Enum('PacketTypes', """data_packet acknowledgement_packet 
                       routing_update_packet fin_packet""")
    
    def __init__(self, src, dest, timestamp, length, packet_type, seq_num):
        """Sets up a network packet with the given specifications:
        
        Args:
            src: Source address.
            dest: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.        
            packet_type: An enum indicating the type of packet ('data packet',
                'acknowledgement_packet', 'routing_update_packet', or
                'fin_packet').
            seq_num: Packet sequence number in a given flow.
        """
        
        self.src = src
        self.dest = dest
        self.timestamp = timestamp
        self.length = length
        self.packet_type = packet_type
        self.seq_num = seq_num
        
    def get_source(self):
        """Returns source address."""
        return self.src
    
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
    
    def get_sequence_number(self):
        """Returns the packet's sequence number relative to a flow."""
        return self.seq_num

    def set_source(self, src):
        """Sets source address."""
        self.src = src
    
    def set_destination(self, dest):
        """Sets destination address."""
        self.dest = dest
        
    def set_length(self, length):
        """Sets the packet length."""
        self.length = length
    
    def set_packet_type(self, packet_type):
        """Sets the packet type."""
        assert(packet_type in Packet.PacketTypes)
        self.packet_type = packet_type
    
    def set_sequence_number(self, seq_num):
        """Sets the packet's sequence number relative to a flow."""
        self.seq_num = seq_num
        
class DataPacket(Packet):
    """Defines the properties and methods of a data packet.

    For the purposes of this simulation, a data packet need not actually contain
    a payload.
    """
    
    def __init__(self, src, dest, timestamp, length, seq_num):
        """Sets up a data packet with the given specifications:
                
        Args:
            src: Source address.
            dest: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            seq_num: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'data_packet'.
        """
        
        super(DataPacket, self).__init__(
            src, dest, timestamp, length, Packet.PacketTypes.data_packet,
            seq_num)

class AckPacket(Packet):
    """Defines the properties and methods of an acknowledgement packet.
    
    An acknowledgment packet will acknowledge a particular data packet through
    its seq_num attribute.
    """
    
    def __init__(self, src, dest, timestamp, length, seq_num):
        """Sets up an acknowledgement packet with the given specifications:
                
        Args:
            src: Source address.
            dest: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            seq_num: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'acknowledgement_packet'.
        """
        
        super(AckPacket, self).__init__(src, dest, timestamp, length,
            Packet.PacketTypes.acknowledgement_packet, seq_num)
        
class RoutingUpdatePacket(Packet):
    """Defines the properties and methods of a routing update packet.
    
    Routers implement dynamic routing through the Bellman-Ford algorithm. Thus,
    a routing update packet will contain a table of distance estimates to each
    router.
    """
    
    def __init__(self, src, dest, timestamp, length, seq_num, dist_estimates):
        """Sets up a routing update packet with the given specifications:
                
        Args:
            src: Source address.
            dest: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            seq_num: Packet sequence number in a given flow.
            dist_estimates: Table of distance estimates to each router as a list
                of tuples [(router ID, distance to router ID from source)].
            
        The packet_type attribute is set to 'routing_update_packet'.
        """
        
        super(RoutingUpdatePacket, self).__init__(
            src, dest, timestamp, length,
            Packet.PacketTypes.routing_update_packet, seq_num)
        
        self.dist_estimates = dist_estimates
        
    def get_distance_estimates(self):
        """Returns the table of distance estimates computed by the source router
        at the given timestamp."""
        return self.dist_estimates

class FINPacket(Packet):
    """Defines the properties and methods of an FIN packet.
    
    A FIN packet signals the termination of a TCP connection.
    """
    
    def __init__(self, src, dest, timestamp, length, seq_num):
        """Sets up a data packet with the given specifications:
                
        Args:
            src: Source address.
            dest: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            seq_num: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'fin_packet'.
        """
        
        super(FINPacket, self).__init__(src, dest, timestamp, length,
            Packet.PacketTypes.fin_packet, seq_num)
