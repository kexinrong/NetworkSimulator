"""AcknowledgementPacket class derived from general Packet class.

An acknowledgment packet will acknowledge a particular data packet through its
sequence_number attribute.
"""

from packet import Packet

class AcknowledgementPacket(Packet):
    """Defines the properties and methods of an acknowledgement packet."""
    
    def __init__(self, source, destination, timestamp, length, sequence_number):
        """Sets up an acknowledgement packet with the given specifications:
                
        Args:
            source: Source address.
            destination: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            sequence_number: Packet sequence number in a given flow.
            
        The packet_type attribute is set to 'acknowledgement_packet'.
        """
        
        super(AcknowledgementPacket, self).__init__(
            source, destination, timestamp, length,
            Packet.PacketTypes.acknowledgement_packet, sequence_number)
