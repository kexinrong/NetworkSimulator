"""Defines the properties and methods of network flow processes."""

from packet import Packet, DataPacket, AckPacket, FINPacket

class Flow(object):
    """
        A flow represents an end-to-end connection. Flows can be of two types:
        receiving and sending flows.  
    """  
    def __init__(self, env, flow_id, dest_host_id=None, src_host=None):
        """
            Sets up a flow object. 
 
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       ID of flow.
                   dest_host_id:
                       ID of host where flow ends.  
                   src_host:
                       Host object where the flow starts.
               
            Attributes: 
                   env, flow_id, src_host, dest_host_id as above.
                   src_host_id:
                       ID of source host.
                   received_packets:
                       List of packets received so far.
                   receive_packet:
                       Internal event triggered when host wants to deliver 
                       packets to the flow.                        
        """
        self.env = env
        self.flow_id = flow_id
        self.src_host = src_host

        if (self.src_host == None):
            self.src_host_id = None
        else:
            self.src_host_id = src_host.get_id()

        self.dest_host_id = dest_host_id

        # Set up received_packets buffer. May be useful for congestion control.
        self.received_packets = []

        # Set up flow's notification event
        self.receive_packet = env.event()      

    def get_id(self):
        """Returns flow ID."""   
        return self.flow_id

    def add_src_host(self, src_host):
        """Add source host after initialization."""
        assert(self.src_host == None)
        self.src_host = src_host
        self.src_host_id = src_host.get_id()

    def add_dest_host_id(self, dest_host_id):
        """Add destination host id after initialization."""
        assert(self.dest_host_id == None)
        self.dest_host_id = dest_host_id

    def receive_packet(self, incoming_packet):
        """Method called by flow's source host to transmit packet to flow."""     
        # Add packet to flow's received_packets buffer.
        self.received_packets.append(incoming_packet)     

        # Trigger notification event to reactivate flow.
        self.receive_packet.succeed()

    def end_flow(self):
        """Remove flow from source host's list of flows."""
        self.src_host.remove_flow(self.flow_id) 

    def notify_collision(seq_num):
        """Called by the host when a packet is not sent due to collision."""
        # Not implemented yet
        pass

class SendingFlow(Flow):
    """
        A sending flow sends data from the source host to destination host.
        It receives acknowledgment packets.

        Attributes:
                     MB_TO_BYTES: Conversion factor.  
                     S_TO_MS: Conversion factor.
                     MS_TO_S: Conversion factor.
                     DATA_PCK_SIZE: Size of data packet in bytes.
    """
    MB_TO_BYTES = 2 ** 20
    S_TO_MS = 1000
    MS_TO_S = 0.001
    DATA_PCK_SIZE = 1024

    def __init__(self, env, flow_id, data_amt_MB, start_time_s, dest_host_id=None, src_host=None):
        """
            Sets up a sending flow object.
           
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       Identification number of flow.
                   data_amt_MB:
                       Amount of data to be transferred in MB. Input uses MB.
                   start_time_s:
                       Time (in seconds) after which flow starts transmitting 
                       data. Input uses seconds.
                   dest_host_id:
                       ID of host where flow ends. 
                   src_host:
                       Host object in which the flow starts.
               
            Attributes:
                   env, flow_id, src_host and dest_host_id as above.
                   src_host_id:
                       ID of source host.
                   data_amt: 
                       Amount of data in bytes the flow needs to send. Bytes 
                       are more convenient to work with since packet sizes are
                       in bytes.
                   start_time: 
                       Time in ms after which flow starts transmitting data. 
                       This is convenient because the environment uses ms.
                   end_time:
                       Time in ms when flow is done transmitting data. Needed 
                       for data reporting.
                   received_packets:
                       List of packets received so far.
                   receive_packet:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.
                   num_packets_sent:
                       Number of packets sent since interval start time.
                   num_packets_received:
                       Number of packets received since interval start time.
                   sum_RTT_delay:
                       Sum of round-trip time delays seen for ack packets 
                       received since interval start time.                             
        """       
        super(SendingFlow, self).__init__(env, flow_id, dest_host_id, src_host)

        self.data_amt = data_amt_MB * SendingFlow.MB_TO_BYTES
        self.start_time = start_time_s * SendingFlow.S_TO_MS
        # Flow has not ended yet.
        self.end_time = None

        # Initiliaze fields for metrics reporting.
        self.num_packets_sent = 0
        self.num_packets_received = 0
        self.sum_RTT_delay = 0

        # Add the run generator to the event queue.
        env.process(self.run(env))

    def run(self, env):
        """
            Implements the functionality of a sending flow.
 
            In this implementation, the flow sends a packet, waits for acknowledgment
            and then sends another packet until there is no more data to send. 
            Data transmission gets stuck if an acknowledment is not received.
        """
        # Passivate until start time.
        yield env.timeout(self.start_time)

        seq_num = 1
        while self.data_amt > 0:
            # Create new packet.
            data_packet = DataPacket(self.src_host_id, self.flow_id, 
                                     self.dest_host_id, env.now, 
                                     seq_num)
  
            # Call host function to send packet, update counter.  
            self.src_host.send_packet(data_packet)
            self.num_packets_sent += 1

            # Passivate until an ack packet is received, update counter.   
            yield self.receive_packet 
            self.num_packets_received += 1
     
            received_packet = self.received_packets[-1]
           
            # Throw an error if received packet is not an ack packet.
            assert(received_packet.get_packet_type() == 
                   Packet.PacketTypes.acknowledgement_packet)           

            # Check if received ack packet has correct seq_num.  
            if (received_packet.get_sequence_number() == seq_num):
                # Update data_amt and seq_num.
                self.data_amt -= SendingFlow.DATA_PCK_SIZE
                seq_num += 1
                # Add RTT delay for data_packet.
                self.sum_RTT_delay += (env.now - data_packet.get_timestamp())

            # Reset event
            self.receive_packet = env.event()
       
        # All the data has been sent. Send FIN packet.
        fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                               self.dest_host_id, env.now, 
                               seq_num)
        self.src_host.send_packet(fin_packet) 
        self.num_packets_sent += 1
        
        # Passivate until a FIN packet is received in response.
        yield self.receive_packet
        self.num_packets_received += 1

        # Throw error if packet is not FIN packet with correct seq_num.
        assert(self.received_packets[-1].get_packet_type() == 
               Packet.PacketTypes.fin_packet)
        assert(self.received_packets[-1].get_sequence_number() == seq_num) 
               
        # End flow.
        self.end_time = env.now
        self.end_flow()   

    def get_reporting_interval():
        """Calculates the appropriate interval (in s) over which averaging 
           is done."""
        # Reporting interval in which flow has started.    
        if (self.env.now - self.env.interval < self.start_time):
            interval = self.env.now - self.start_time
        # Reporting interval in which flow has ended.
        elif (self.end_time != None and 
                 self.env.now - self.env.interval < self.end_time):
            interval = self.end_time - self.env.now + self.env.interval
        # All other reporting intervals. Includes interval in which flow
        # has not started or has ended in a previous interval.
        else:
            interval = self.env.interval

        return interval * SendingFlow.MS_TO_S

    def report(self):
        """Report average flow send/receive rate (in packets/s) and average RTT
           delay (in ms) since start of flow/last time report was called.

           If no packets are received in a reporting interval, the avg_RTT_delay
           us reported to be 0.

           If the flow has not yet started or it has ended in a previous 
           reporting interval, (0, 0, 0) is returned.
        """     
        # Time passed in s.
        time_interval = get_reporting_interval()
        assert(time_interval > 0)

        # Calculate send/receive rates (packets/s) and average RTT (in ms).
        flow_send_rate = self.num_packets_sent / time_interval
        flow_receive_rate = self.num_packets_received / time_interval
        
        if (self.num_packets_received > 0):
            flow_avg_RTT = self.sum_RTT_delay / self.num_packets_received
        else:
            flow_avg_RTT = 0

        # Reset counters.
        self.num_packets_sent = 0
        self.num_packets_received = 0
        self.sum_RTT_delay = 0

        return {'flow_send_rate' : flow_send_rate,
                'flow_receive_rate' : flow_receive_rate,
                'flow_avg_RTT' : flow_avg_RTT}
               
class ReceivingFlow(Flow):
    """
        A receiving flow receives data packets and sends acknowledgments.
    """
    def __init__(self, env, flow_id, dest_host_id=None, src_host=None):
        """
            Sets up a receiving flow object.
           
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       Identification number of flow (same as corresponding 
                       sending flow).
                   dest_host_id:
                       ID of host where flow ends. 
                   src_host:
                       Host object in which the flow starts.               
            Attributes:
                   env, flow_id, src_host and dest_host_id as above.
                   src_host_id:
                       ID of source host.
                   received_packets:
                       List of packets received so far.
                   receive_packet:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.

        """       
        super(ReceivingFlow, self).__init__(env, flow_id, dest_host_id, src_host)

        # Add the run generator to the event queue.
        self.env.process(self.run(env))

    def run(self, env):
        """
            Implements the functionality of a receiving flow.

            In this implementation, the flow simply sends an ACK packet upon
            receiving a data packet. 
        """
        while True:
             # Passivate until packet received.
            yield self.receive_packet
            
            received_packet = self.received_packets[-1]
            if (received_packet.get_packet_type() == Packet.PacketTypes.data_packet):
                # Create new ack packet with same seq_num as received data packet.
                ack_packet = AckPacket(self.src_host_id, self.flow_id, 
                                       self.dest_host_id, env.now, 
                                       received_packet.get_sequence_number())
      
                # Call host function to send packet.  
                self.src_host.send_packet(ack_packet)

                # Reset event.
                self.receive_packet = env.event()

            else: 
                # Throw error if packet is not a FIN_packet
                assert(received_packet.get_packet_type() == 
                       Packet.PacketTypes.fin_packet)
                # FIN_packet received. Send FIN_packet in response.
                fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                                       self.dest_host_id, env.now, 
                                       received_packet.get_sequence_number())
                self.src_host.send_packet(fin_packet)
                break     
       
        self.end_flow()
