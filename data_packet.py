"""DataPacket class derived from general Packet class.

For the purposes of this simulation, a data packet need not actually contain a
payload.
"""

from packet import Packet

class DataPacket(Packet):
    """Defines the properties and methods of a data packet."""
    
    def __init__(self, source, destination, timestamp, length, sequence_number):
        """Sets up a data packet with the given specifications:
                
        Args:
            source: Source address.
            destination: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            sequence_number: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'data_packet'.
        """
        
        super(DataPacket, self).__init__(
            source, destination, timestamp, length,
            Packet.PacketTypes.data_packet, sequence_number)
