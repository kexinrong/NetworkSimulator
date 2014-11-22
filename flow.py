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
                   receive_packet_event:
                       Internal event triggered when host wants to deliver 
                       packets to the flow.
                   num_packets_received:
                       Number of packets received since interval start time. Needed
                       to calculate RTT delay.                 
                   amt_data_sent:   
                       Data sent since interval start time (in bytes).
                   amt_data_received:
                       Data received since interval start time (in bytes).
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

        # Initialize for metrics reporting.
        self.num_packets_received = 0
        self.amt_data_sent = 0
        self.amt_data_received = 0

        # Set up flow's notification event
        self.receive_packet_event = env.event()      

    def get_id(self):
        """Returns flow ID."""   
        return self.flow_id

    def add_src_host(self, src_host):
        """Add source host after initialization."""
        assert(self.src_host == None and src_host != None)
        self.src_host = src_host
        self.src_host_id = src_host.get_id()

    def add_dest_host_id(self, dest_host_id):
        """Add destination host id after initialization."""
        assert(self.dest_host_id == None)
        self.dest_host_id = dest_host_id

    def receive_packet(self, incoming_packet):
        """Method called by flow's source host to transmit packet to flow."""     
        # Debug message
        #print self.get_flow_type() + " " + str(self.get_id()) + " receiving " + \
        #      incoming_packet.packet_type_str() + " packet_" + \
        #      str(incoming_packet.get_seq_num())  
  
        # Add packet to flow's received_packets buffer.
        self.received_packets.append(incoming_packet)
        self.num_packets_received += 1      
        self.amt_data_received += incoming_packet.get_length()

        # Trigger notification event to reactivate flow.
        if not self.receive_packet_event.triggered:
            self.receive_packet_event.succeed()

    def send_packet(self, outgoing_packet):
        """Method called by flow to send packet."""
        # Debug message
        #print
        #print self.get_flow_type() + " " + str(self.get_id()) + " sending " + \
        #      outgoing_packet.packet_type_str() + " packet_" + \
        #      str(outgoing_packet.get_seq_num()) 

        self.src_host.send_packet(outgoing_packet)
        self.amt_data_sent += outgoing_packet.get_length()

    def end_flow(self):
        """Remove flow from source host's list of flows."""
        # Debug message
        #print self.get_flow_type() + " " + str(self.get_id()) + " ending." 
        #self.src_host.remove_flow(self.flow_id) 

class SendingFlow(Flow):
    """
        A sending flow sends data from the source host to destination host.
        It receives acknowledgment packets.

        Attributes:
               MB_TO_BYTES: Conversion factor. 
               B_TO_MBITS: Conversion factor 
               S_TO_MS: Conversion factor.
               MS_TO_S: Conversion factor.
               DATA_PCK_SIZE: Size of data packet in bytes.
    """
    MB_TO_BYTES = 2 ** 20
    B_TO_MBITS = 1.0/(MB_TO_BYTES) * 8
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
                   congestion_control:
                       congestion control algorithm for the flow
               
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
                   receive_packet_event:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.
                   received_fin_event:
                       Internal event triggered when a fin packet has been received. 
                   received_batch_event:
                       Internal event triggered when ack packets for all outstanding
                       packets have been received.
                   num_packets_received:
                       Number of packets received since interval start time.
                   amt_data_sent:
                       Amount of data sent since interval start time (in bytes).
                   amt_data_received:
                       Amount of data received since interval start time (in bytes).
                   sum_RTT_delay:
                       Sum of round-trip time delays seen for ack packets 
                       received since interval start time.        
                   window_size: 
                       Window size for transmission.
                   retransmit_timeout: 
                       Timeout (in ms) for retransmission if no ack packet is received.  
                   num_unack_packets: 
                       Number of unacknowledged packets.     
                   batch_start: 
                       Sequence number of first data packet in current batch. 
                   batch_end:
                       Sequence number of last data packet in current batch.       
                   ack_dict: 
                       Dictionary with keys as sequence numbers of data packets  
                       in current batch and boolean values indicating if 
                       an ack packet has been received for it. 
                   rtt:
                         RTT of the latest packet (in ms)
   
                   (FAST specific parameters)
                     base_rtt:
                         minimum RTT seen so far (in ms)
                     alpha:
                        parameter for FAST TCP
                     fast_timeout:
                        interval for FAST to adjust window size (in ms)

                   (Tahoe specific parameters)
                     ssthresh:
                         threshold for congestion avoidance
                     is_CA:
                         whether we are in congestion control right now
        """       
        super(SendingFlow, self).__init__(env, flow_id, dest_host_id, src_host)

        self.data_amt = data_amt_MB * SendingFlow.MB_TO_BYTES
        self.start_time = start_time_s * SendingFlow.S_TO_MS
        # Flow has not ended yet.
        self.end_time = None
        # Congestion control algorithm
        self.cc = congestion_control

        # Notification event. 
        self.received_fin_event = env.event()
        self.received_batch_event = env.event()  

        # Default window size and timeout.
        if self.cc == "FAST":
            self.window_size = 100
        else:
            # Slow start for Tahoe
            self.window_size = 1
        self.retransmit_timeout = 3000 # Default to 3s
     
        # Initialize fields for packet accounting.
        self.num_unack_packets = 0
        self.batch_start = 1
        self.batch_end = None
        self.ack_dict = {}        

        # Initialize field for metrics reporting.
        self.sum_RTT_delay = 0
        self.rtt = None

        # FAST parameters
        if self.cc == "FAST":
            self.base_rtt = 100000
            self.alpha = 15
            self.fast_timeout = 1000 # Update window size every second
        else:
            self.is_CA = False
            self.ssthresh = 40

        # Add the run generator to the event queue.
        env.process(self.run(env))
    
    def set_window_size(self, window_size):
        """Sets window size to some whole number.""" 
        assert(window_size > 0)
        self.window_size = window_size

    def set_retransmit_timeout(self, retransmit_timeout):
        """Sets retransmit timeout (in ms)."""
        assert(retransmit_timeout > 0)
        self.retransmit_timeout = retransmit_timeout

    def FAST(self, env):
        ''' Congestion control algorithm using FAST TCP '''
        while True:
          yield env.timeout(self.fast_timeout)
          # Adjust window size
          self.window_size = self.window_size * self.base_rtt * 1.0 / self.rtt \
              + self.alpha

    def run(self, env):
        """
            Implements the functionality of a sending flow.

            In this implementation, the flow follows the Go-Back-N ARQ
            protocol. 
            It sends window_size number of packets and waits until 
            retransmit_timeout or all ack packets are received. 
            Then the flow sends window_size number of packets starting 
            from batch_start. 
            
            batch_start is initially 1. It is incremented when an ack
            packet for batch_start is received. 
        """
        # Passivate until start time.
        yield env.timeout(self.start_time)
  
        # Process to handle incoming packets.
        if self.cc == "FAST":
            env.process(self.FAST_monitor_incoming_pkts(env))
            env.process(self.FAST(env))
        else:
            env.process(self.tahoe_monitor_incoming_pkts(env))
 
        while self.data_amt > 0:
            self.send_data()
            # Passivate until all ack packets received or timeout occurs. 
            yield self.received_batch_event | env.timeout(self.retransmit_timeout)
            # Tahoe - packet loss
            if self.cc == "Tahoe" and self.num_unack_packets > 0:
                self.ssthresh = self.window_size / 2.0
                self.window_size = 1
                self.is_CA = False
            elif (self.received_batch_event.triggered):
                self.received_batch_event = env.event()
            # Adjust retransmit timeout
            self.set_retransmit_timeout(3 * self.rtt)


        # All the data has been sent. Send FIN packet.
        fin_resend = True
        while fin_resend:
            fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                                   self.dest_host_id, env.now, 
                                   self.batch_end + 1)
            self.send_packet(fin_packet)
            # Passivate until a FIN packet is received or timeout occurs.
            yield self.received_fin_event | env.timeout(self.retransmit_timeout)         
            if (self.received_fin_event.triggered):
                fin_resend = False            
   
        # End flow.
        self.end_time = env.now
        self.end_flow()      
        
    def FAST_monitor_incoming_pkts(self, env):
        """ Process to handle incoming packets for FAST """
        while self.data_amt > 0:
            yield self.receive_packet_event
            received_packet = self.received_packets.pop()
         
            # Throw error if packet not an ack packet.
            assert(received_packet.get_packet_type() == 
                    Packet.PacketTypes.ack_packet)   
            
            rec_seq_num = received_packet.get_seq_num()     
            
            # Update current RTT, base RTT, sum RTT
            self.rtt = self.env.now - received_packet.get_timestamp()
            self.base_rtt = min(self.rtt, self.base_rtt) 
            self.sum_RTT_delay += self.rtt
           
            # Reset event
            self.receive_packet_event = env.event()

            if (self.ack_dict.has_key(rec_seq_num) and  
                self.ack_dict[rec_seq_num] == False):

                self.ack_dict[rec_seq_num] = True
                self.num_unack_packets -= 1 
                # Update batch start if necessary.
                if (rec_seq_num == self.batch_start):
                    self.batch_start += 1
                    self.data_amt -= SendingFlow.DATA_PCK_SIZE   
                                           
            if (self.num_unack_packets == 0):
                self.received_batch_event.succeed()
        
        yield self.receive_packet_event
        received_packet = self.received_packets.pop()   
        
        if (received_packet.get_packet_type() == 
                Packet.PacketTypes.fin_packet):     
            assert(received_packet.get_seq_num() == self.batch_end + 1)
            self.received_fin_event.succeed() 

    def tahoe_monitor_incoming_pkts(self, env):
        """ Process to handle incoming packets for Tahoe """
        while self.data_amt > 0:
            yield self.receive_packet_event
            received_packet = self.received_packets.pop()

            # Throw error if packet not an ack packet.
            assert(received_packet.get_packet_type() ==
                    Packet.PacketTypes.ack_packet)

            rec_seq_num = received_packet.get_seq_num()

            # Update sum RTT
            self.rtt = self.env.now - received_packet.get_timestamp()
            self.sum_RTT_delay += self.rtt

            # Reset event
            self.receive_packet_event = env.event()

            if (self.ack_dict.has_key(rec_seq_num) and
                self.ack_dict[rec_seq_num] == False):

                self.ack_dict[rec_seq_num] = True
                self.num_unack_packets -= 1
                # For successful ack, update batch start if necessary
                # and adjust window size
                if (rec_seq_num == self.batch_start):
                    self.batch_start += 1
                    self.data_amt -= SendingFlow.DATA_PCK_SIZE
                    # CA
                    if self.is_CA:
                        self.window_size += 1.0 / self.window_size
                    # SS
                    else:
                        self.window_size += 1
                        if self.window_size >= self.ssthresh:
                            self.is_CA = True

            if (self.num_unack_packets == 0):
                self.received_batch_event.succeed()

        yield self.receive_packet_event
        received_packet = self.received_packets.pop()

        if (received_packet.get_packet_type() ==
                Packet.PacketTypes.fin_packet):
            assert(received_packet.get_seq_num() == self.batch_end + 1)
            self.received_fin_event.succeed()


    def send_data(self):
        """Sends a batch of data packets starting at batch_start."""
        count = 0
        data_sent = 0
        self.ack_dict = {}
        seq_num = self.batch_start
          
        while (count < self.window_size and data_sent < self.data_amt):
            data_packet = DataPacket(self.src_host_id, self.flow_id, 
                                     self.dest_host_id, self.env.now,
                                     seq_num)      
            self.send_packet(data_packet)
            self.ack_dict[seq_num] = False
            seq_num += 1
            count += 1
            data_sent += SendingFlow.DATA_PCK_SIZE
                              
        self.num_unack_packets = count
        self.batch_end = seq_num - 1  
        print str(self.get_id()) + " sent data packet " + \
          str(self.batch_start) + " to " + str(self.batch_end)

    def get_reporting_interval(self):
        """Calculates the appropriate interval (in s) over which averaging 
           is done."""
        # Reporting interval in which flow has started.    
        if (self.env.now - self.env.interval < self.start_time
            and self.env.now > self.start_time):
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
        """Report average flow send/receive rate (in Mbps) and average RTT
           delay (in ms) since start of flow/last time report was called.

           Also, report window size.

           If no packets are received in a reporting interval, the avg_RTT_delay
           is reported to be 0.

           If the flow has not yet started or it has ended in a previous 
           reporting interval, (0, 0, 0) is returned.
        """     
        # Time passed in s.
        time_interval = self.get_reporting_interval()
        assert(time_interval > 0)

        # Calculate send/receive rates (Mbps) and average RTT (in ms).
        flow_send_rate = (self.amt_data_sent * SendingFlow.B_TO_MBITS) / time_interval
        flow_receive_rate = (self.amt_data_received * SendingFlow.B_TO_MBITS) / time_interval
        
        window_size = self.window_size
        if (self.num_packets_received > 0):
            flow_avg_RTT = self.sum_RTT_delay / self.num_packets_received
        else:
            flow_avg_RTT = 0
            window_size = 0

        # Reset counters.
        self.num_packets_received = 0
        self.amt_data_sent = 0
        self.amt_data_received = 0
        self.sum_RTT_delay = 0

        return {'flow_send_rate' : flow_send_rate,
                'flow_receive_rate' : flow_receive_rate,
                'flow_avg_RTT' : flow_avg_RTT,
                'flow_window_size' : window_size}
               
    def get_flow_type(self):
        """ Helper function to get flow type. """
        return "SendingFlow"

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
                   receive_packet_event:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.
                   num_packets_sent:
                       Number of packets sent since interval start time. Needed
                       to calculate RTT delay.                 
                   amt_data_sent:   
                       Data sent since interval start time (in bytes).
                   amt_data_received:
                       Data received since interval start time (in bytes).
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
            yield self.receive_packet_event

            received_packet = self.received_packets.pop()                       
            if (received_packet.get_packet_type() == Packet.PacketTypes.data_packet):
                # Create new ack packet with same seq_num as received data packet.
                # ack packet has the same timestamp as the corresponding data packet.
                # This is useful for calculating RTT delay.
                ack_packet = AckPacket(self.src_host_id, self.flow_id, 
                                       self.dest_host_id, received_packet.get_timestamp(), 
                                       received_packet.get_seq_num())
      
                # Send packet.  
                self.send_packet(ack_packet)

                # Reset event.
                self.receive_packet_event = env.event()

            else: 
                # Throw error if packet is not a FIN_packet
                assert(received_packet.get_packet_type() == 
                       Packet.PacketTypes.fin_packet)
                # FIN_packet received. Send FIN_packet in response.
                fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                                       self.dest_host_id, received_packet.get_timestamp(), 
                                       received_packet.get_seq_num())
                self.send_packet(fin_packet)
                break     
       
        self.end_flow()

    def get_flow_type(self):
        """ Helper function to get flow type """
        return "ReceivingFlow"
