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
    
    def __init__(self, source, destination, timestamp, length, packet_type,
                 sequence_number):
        """Sets up a network packet with the given specifications:
        
        Args:
            source: Source address.
            destination: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.        
            packet_type: An enum indicating the type of packet ('data packet',
                'acknowledgement_packet', 'routing_update_packet', or
                'fin_packet').
            sequence_number: Packet sequence number in a given flow.
        """
        
        self.source = source
        self.destination = destination
        self.timestamp = timestamp
        self.length = length
        self.packet_type = packet_type
        self.sequence_number = sequence_number
        
    def get_source(self):
        """Returns source address."""
        return self.source
    
    def get_destination(self):
        """Returns destination address."""
        return self.destination
    
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
        return self.sequence_number

    def set_source(self, source):
        """Sets source address."""
        self.source = source
    
    def set_destination(self, destination):
        """Sets destination address."""
        self.destination = destination
        
    def set_length(self, length):
        """Sets the packet length."""
        self.length = length
    
    def set_packet_type(self, packet_type):
        """Sets the packet type."""
        assert(packet_type in Packet.PacketTypes)
        self.packet_type = packet_type
    
    def set_sequence_number(self, sequence_number):
        """Sets the packet's sequence number relative to a flow."""
        self.sequence_number = sequence_number
