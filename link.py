from collections import deque
from packet import Packet

class Link(object):
    # Conversion constants from Mbps to bytes per milisecond
    MBPS_TO_B_PER_MS = 131.072
    KB_TO_B = 1024

    def __init__(self, env, id, link_rate, link_delay,
                 buffer_size, end_points=None):
        """ Attributes:
                env:
                    SimPy environment in which everything resides.
                id:
                    id for this link
                link_rate:
                    link rate converted to bytes per milisecond
                link_delay:
                    link delay in ms
                buffer_size:
                    buffer size in bytes
                end_points:
                    a tuple of objects that the link connects to
                buffer:
                    a deque object which models the buffer queue
                buffer_used:
                    total size of the packets in the buffer
                transmitted_size:
                    size of packets transmitted since the last
                    statictics collection in Bytes
                busy:
                    event that indicates whether link is busy
        """
        self.env = env
        self.id = id
        # Link rate in bytes per milisecond
        self.link_rate =  Link.MBPS_TO_B_PER_MS * link_rate
        self.link_delay = link_delay
        # Buffer size in Bytes
        self.buffer_size = Link.KB_TO_B * buffer_size

        self.buffer = {}
        self.buffer_used = {}
        self.end_points = end_points
        if end_points:
            self.add_end_points(end_points)

        # Statistics collection
        self.packet_drop = 0
        self.transmitted_size = 0

        # reactive event and processes
        self.busy = env.event()
        env.process(self.transmit(env))

    def add_end_points(self, end_points):
        """ Mutator funciton to add end points to link """
        # ids of endpoints
        self.device_ids = [end_points[0].get_id(), end_points[1].get_id()]
        # Buffer on both sides
        self.buffer[self.device_ids[0]] = deque()
        self.buffer[self.device_ids[1]] = deque()
        # Buffer occupied on both sides
        self.buffer_used[self.device_ids[0]] = 0
        self.buffer_used[self.device_ids[1]] = 0

    def get_id(self):
        """ Function that returns link id. """
        return self.id

    def enqueue(self, packet, src_id):
        """ Function to handle incoming packets: drop the
            packet if buffer is full, otherwise enqueue the packet
            and wake up process() 
        """
        size = packet.get_length()
        # Drop the packet if buffer is full
        if self.buffer_used[src_id] + size > self.buffer_size:
            self.packet_drop += 1
        else:
            self.buffer[src_id].append((packet, self.env.now))
            self.buffer_used[src_id] += size
            if not self.busy.triggered:
                # Wake up link 
                self.busy.succeed()

    def buffer_empty(self):
        """ Helper function to check whether both buffers
            are empty. 
        """
        return len(self.buffer[self.device_ids[0]]) + \
               len(self.buffer[self.device_ids[1]]) == 0

    def find_next_packet(self):
        """ Helper function that returns the index of the buffer from 
            which the next packet should be transmitted
        """
        if len(self.buffer[self.device_ids[0]]) == 0:
            return 1
        elif len(self.buffer[self.device_ids[1]]) == 0:
            return 0
        else:
            # Peek the leftmost packets on both buffers
            packet_1, ts_1 = self.buffer[self.device_ids[0]][0]
            packet_2, ts_2 = self.buffer[self.device_ids[1]][0]
            if ts_1 <= ts_2:
                return 0
            else:
                return 1

    def transmit(self, env):
        """ Processs to transmit packets from both buffers.
            The transmit is done by always sending the packet  
            that arrived first in the buffer.
        """
        while True:
            yield self.busy
          
            while not self.buffer_empty():
                idx = self.find_next_packet()
                # peek at leftmost packet
                packet, ts = self.buffer[self.device_ids[idx]][0]
                size = packet.get_length()
                # size / self.link_rate is in ms
                yield env.timeout(size / self.link_rate)
                self.buffer_used[self.device_ids[idx]] -= size
                self.buffer[self.device_ids[idx]].popleft()
                # Schedule event after link_delay
                env.process(self.send_packet(idx, packet))
                self.transmitted_size += size

            self.busy = self.env.event()  

    def send_packet(self, idx, packet):
        ''' Independent process to schedule receive packet event for host. '''
        yield self.env.timeout(self.link_delay)
        self.end_points[1 - idx].receive_packet(packet)
        
    def get_buffer_size(self):
        """Returns the buffer size of the link in bytes."""
        return self.buffer_size

    def get_buffer_occupancy(self):
        """ Helper function that calculates the total buffer occupancy 
            for link 
        """
        return (self.buffer_used[self.device_ids[0]] + \
               self.buffer_used[self.device_ids[1]]) / (self.buffer_size * 2.0)
    
    def get_weight(self):
        """ Link weight for dynamic routing. """
        return (self.buffer_used[self.device_ids[0]] +
                self.buffer_used[self.device_ids[1]]) / \
                self.link_rate + self.link_delay
    
    def get_link_rate(self):
        """Returns the link rate."""
        return self.link_rate

    def get_flow_rate(self):
        """ Helper function that calculates average flow rate since we
            last called the report function 
        """
        # Convert B/ms to Mbps
        return self.transmitted_size / \
               (Link.MBPS_TO_B_PER_MS * self.env.interval)

    def report(self):
        """ Function that reports link statictics to environment """
        # Convert buffer occupancy to percentage
        buffer_occ = 100 * self.get_buffer_occupancy()
        flow_rate = self.get_flow_rate()
        packet_drop = self.packet_drop
        # Clear transmitted_size and packet drop for the next round
        self.transmitted_size = 0
        self.packet_drop = 0
        return {'packet_loss' : packet_drop,
                'buffer_occupancy' : buffer_occ,
                'link_rate' : flow_rate}
