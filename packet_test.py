import unittest
from packet import Packet, DataPacket, AcknowledgementPacket, \
     RoutingUpdatePacket, FINPacket

class PacketTest(unittest.TestCase):
    """Test definitions and methods of Packet base class."""
    
    # Various test constants
    SOURCE_ADDRESS = 1
    DESTINATION_ADDRESS = 2
    TIMESTAMP = 30
    LENGTH = 64
    PACKET_TYPE = Packet.PacketTypes.data_packet
    SEQUENCE_NUMBER = 15
    NEW_SOURCE_ADDRESS = 10
    NEW_DESTINATION_ADDRESS = 20
    NEW_LENGTH = 256
    NEW_PACKET_TYPE = Packet.PacketTypes.acknowledgement_packet
    NEW_SEQUENCE_NUMBER = 49
    DISTANCE_ESTIMATES = [(1, 0), (2, 3), (3, 10), (4, 11)]
    
    def setUp(self):
        self.packet = Packet(self.SOURCE_ADDRESS, self.DESTINATION_ADDRESS,
            self.TIMESTAMP, self.LENGTH, self.PACKET_TYPE, self.SEQUENCE_NUMBER)
        self.data_packet = DataPacket(self.SOURCE_ADDRESS,
            self.DESTINATION_ADDRESS, self.TIMESTAMP, self.LENGTH,
            self.SEQUENCE_NUMBER)
        self.acknowledgement_packet = AcknowledgementPacket(self.SOURCE_ADDRESS,
            self.DESTINATION_ADDRESS, self.TIMESTAMP, self.LENGTH,
            self.SEQUENCE_NUMBER)
        self.routing_update_packet = RoutingUpdatePacket(self.SOURCE_ADDRESS,                           
            self.DESTINATION_ADDRESS, self.TIMESTAMP, self.LENGTH,
            self.SEQUENCE_NUMBER, self.DISTANCE_ESTIMATES)
        self.fin_packet = FINPacket(self.SOURCE_ADDRESS,
            self.DESTINATION_ADDRESS, self.TIMESTAMP, self.LENGTH,
            self.SEQUENCE_NUMBER)
        
    def test_initialization(self):
        """Checks that packets are initialized with correct specifications.
        This tests the correctness of the accessors in the process.
        """
        
        self.assertEqual(self.SOURCE_ADDRESS, self.packet.get_source())
        self.assertEqual(self.DESTINATION_ADDRESS,
                         self.packet.get_destination())
        self.assertEqual(self.TIMESTAMP, self.packet.get_timestamp())        
        self.assertEqual(self.LENGTH, self.packet.get_length())
        self.assertEqual(self.PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.data_packet,
                         self.data_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.acknowledgement_packet,
                         self.acknowledgement_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.routing_update_packet,
                         self.routing_update_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.fin_packet,
                         self.fin_packet.get_packet_type())
        self.assertEqual(self.SEQUENCE_NUMBER,
                         self.packet.get_sequence_number())
        self.assertCountEqual(self.DISTANCE_ESTIMATES,
            self.routing_update_packet.get_distance_estimates())
        
    def test_mutators(self):
        """Checks that packet attributes are modified correctly."""
        
        # Mutate packet fields.
        self.packet.set_source(self.NEW_SOURCE_ADDRESS)
        self.packet.set_destination(self.NEW_DESTINATION_ADDRESS)
        self.packet.set_length(self.NEW_LENGTH)
        self.packet.set_packet_type(self.NEW_PACKET_TYPE)
        self.packet.set_sequence_number(self.NEW_SEQUENCE_NUMBER)
        
        # Check packet fields have been updated correctly.
        self.assertEqual(self.NEW_SOURCE_ADDRESS, self.packet.get_source())
        self.assertEqual(self.NEW_DESTINATION_ADDRESS,
                         self.packet.get_destination())
        self.assertEqual(self.NEW_LENGTH, self.packet.get_length())
        self.assertEqual(self.NEW_PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(self.NEW_SEQUENCE_NUMBER,
                         self.packet.get_sequence_number())

if __name__ == '__main__':
    unittest.main()
