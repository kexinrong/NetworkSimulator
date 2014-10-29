"""FINPacket class derived from general Packet class.

A FIN packet signals the termination of a TCP connection.
"""

from packet import Packet

class FINPacket(Packet):
    """Defines the properties and methods of an FIN packet."""
    
    def __init__(self, source, destination, timestamp, length, sequence_number):
        """Sets up a data packet with the given specifications:
                
        Args:
            source: Source address.
            destination: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            sequence_number: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'fin_packet'.
        """
        
        super(FINPacket, self).__init__(source, destination, timestamp, length,
            Packet.PacketTypes.fin_packet, sequence_number)
