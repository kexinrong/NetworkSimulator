"""RoutingUpdatePacket class derived from general Packet class.

Routers implement dynamic routing through the Bellman-Ford algorithm. Thus, a
routing update packet will contain a table of distance estimates to each router.
"""

from packet import Packet

class RoutingUpdatePacket(Packet):
    """Defines the properties and methods of a routing update packet."""
    
    def __init__(self, source, destination, timestamp, length, sequence_number,
                 distance_estimates):
        """Sets up a routing update packet with the given specifications:
                
        Args:
            source: Source address.
            destination: Destination address.
            timestamp: Time upon sending packet.
            length: Length of the packet in bytes.
            sequence_number: Packet sequence number in a given flow.
            distance_estimates: Table of distance estimates to each router as a
                list of tuples [(router ID, distance to router ID from source)].
            
        The packet_type attribute is set to 'routing_update_packet'.
        """
        
        super(RoutingUpdatePacket, self).__init__(
            source, destination, timestamp, length,
            Packet.PacketTypes.routing_update_packet, sequence_number)
        
        self.distance_estimates = distance_estimates
        
    def get_distance_estimates(self):
        """Returns the table of distance estimates computed by the source router
        at the given timestamp."""
        return self.distance_estimates
