import sys
sys.path.append('../')
import unittest
from packet import Packet, DataPacket, AckPacket, RoutingUpdatePacket, FINPacket

class PacketTest(unittest.TestCase):
    """Test definitions and methods of Packet base class."""
    
    # Various test constants
    SRC = 1
    DEST = 2
    TIMESTAMP = 30
    LENGTH = 64
    PACKET_TYPE = Packet.PacketTypes.data_packet
    SEQ_NUM = 15
    NEW_SRC = 10
    NEW_DEST = 20
    NEW_LENGTH = 256
    NEW_PACKET_TYPE = Packet.PacketTypes.acknowledgement_packet
    NEW_SEQ_NUM = 49
    DIST_ESTIMATES = [(1, 0), (2, 3), (3, 10), (4, 11)]
    
    def setUp(self):
        self.packet = Packet(self.SRC, self.DEST, self.TIMESTAMP, self.LENGTH,
                             self.PACKET_TYPE, self.SEQ_NUM)
        self.data_packet = DataPacket(self.SRC, self.DEST, self.TIMESTAMP,
                                      self.LENGTH, self.SEQ_NUM)
        self.ack_packet = AckPacket(self.SRC, self.DEST, self.TIMESTAMP,
                                    self.LENGTH, self.SEQ_NUM)
        self.routing_update_packet = RoutingUpdatePacket(self.SRC, self.DEST,
            self.TIMESTAMP, self.LENGTH, self.SEQ_NUM, self.DIST_ESTIMATES)
        self.fin_packet = FINPacket(self.SRC, self.DEST, self.TIMESTAMP,
                                    self.LENGTH, self.SEQ_NUM)
        
    def test_initialization(self):
        """Checks that packets are initialized with correct specifications.
        This tests the correctness of the accessors in the process.
        """
        
        self.assertEqual(self.SRC, self.packet.get_source())
        self.assertEqual(self.DEST, self.packet.get_destination())
        self.assertEqual(self.TIMESTAMP, self.packet.get_timestamp())        
        self.assertEqual(self.LENGTH, self.packet.get_length())
        self.assertEqual(self.PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.data_packet,
                         self.data_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.acknowledgement_packet,
                         self.ack_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.routing_update_packet,
                         self.routing_update_packet.get_packet_type())
        self.assertEqual(Packet.PacketTypes.fin_packet,
                         self.fin_packet.get_packet_type())
        self.assertEqual(self.SEQ_NUM, self.packet.get_sequence_number())
        self.assertCountEqual(self.DIST_ESTIMATES,
            self.routing_update_packet.get_distance_estimates())
        
    def test_mutators(self):
        """Checks that packet attributes are modified correctly."""
        
        # Mutate packet fields.
        self.packet.set_source(self.NEW_SRC)
        self.packet.set_destination(self.NEW_DEST)
        self.packet.set_length(self.NEW_LENGTH)
        self.packet.set_packet_type(self.NEW_PACKET_TYPE)
        self.packet.set_sequence_number(self.NEW_SEQ_NUM)
        
        # Check packet fields have been updated correctly.
        self.assertEqual(self.NEW_SRC, self.packet.get_source())
        self.assertEqual(self.NEW_DEST, self.packet.get_destination())
        self.assertEqual(self.NEW_LENGTH, self.packet.get_length())
        self.assertEqual(self.NEW_PACKET_TYPE, self.packet.get_packet_type())
        self.assertEqual(self.NEW_SEQ_NUM, self.packet.get_sequence_number())

if __name__ == '__main__':
    unittest.main()
