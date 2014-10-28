import unittest
from packet import Packet

class PacketTest(unittest.TestCase):
    """Test definitions and methods of Packet base class."""
    
    """Various test constants."""
    SOURCE_ADDRESS = 1
    DESTINATION_ADDRESS = 2
    SIZE = 64
    PACKET_TYPE = Packet.PacketTypes.data_packet
    SEQUENCE_NUMBER = 15
    NEW_SOURCE_ADDRESS = 10
    NEW_DESTINATION_ADDRESS = 20
    NEW_SIZE = 256
    NEW_PACKET_TYPE = Packet.PacketTypes.acknowledgement_packet
    NEW_SEQUENCE_NUMBER = 49
    
    def setUp(self):
        self.packet = Packet(self.SOURCE_ADDRESS, self.DESTINATION_ADDRESS,
                        self.SIZE, self.PACKET_TYPE, self.SEQUENCE_NUMBER)
        
    def test_initialization(self):
        """Checks that packets are initialized with correct specifications.
        This tests the correctness of the accessors in the process.
        """
        self.assertEqual(self.SOURCE_ADDRESS, self.packet.get_source())
        self.assertEqual(self.DESTINATION_ADDRESS,
                         self.packet.get_destination())
        self.assertEqual(self.SIZE, self.packet.get_size())
        self.assertEqual(self.PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(self.SEQUENCE_NUMBER,
                         self.packet.get_sequence_number())
        
    def test_mutators(self):
        """Checks that packet attributes are modified correctly."""
        # Mutate packet fields.
        self.packet.set_source(self.NEW_SOURCE_ADDRESS)
        self.packet.set_destination(self.NEW_DESTINATION_ADDRESS)
        self.packet.set_size(self.NEW_SIZE)
        self.packet.set_packet_type(self.NEW_PACKET_TYPE)
        self.packet.set_sequence_number(self.NEW_SEQUENCE_NUMBER)
        
        # Check packet fields have been updated correctly.
        self.assertEqual(self.NEW_SOURCE_ADDRESS, self.packet.get_source())
        self.assertEqual(self.NEW_DESTINATION_ADDRESS,
                         self.packet.get_destination())
        self.assertEqual(self.NEW_SIZE, self.packet.get_size())
        self.assertEqual(self.NEW_PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(self.NEW_SEQUENCE_NUMBER,
                         self.packet.get_sequence_number())
    
if __name__ == '__main__':
    unittest.main()
