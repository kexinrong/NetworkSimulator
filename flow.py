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
                       Number of packets received since intervak start time. Needed
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
        assert(self.src_host == None)
        self.src_host = src_host
        self.src_host_id = src_host.get_id()

    def add_dest_host_id(self, dest_host_id):
        """Add destination host id after initialization."""
        assert(self.dest_host_id == None)
        self.dest_host_id = dest_host_id

    def receive_packet(self, incoming_packet):
        """Method called by flow's source host to transmit packet to flow."""     
        # Debug message
        print self.get_flow_type() + " " + str(self.get_id()) + " receiving " + \
              incoming_packet.packet_type_str() + " packet_" + \
              str(incoming_packet.get_seq_num())  
  
       # Add packet to flow's received_packets buffer.
        self.received_packets.append(incoming_packet)
        self.num_packets_received += 1      
        self.amt_data_received += incoming_packet.get_length()

        # Trigger notification event to reactivate flow.
        self.receive_packet_event.succeed()

    def send_packet(self, outgoing_packet):
        """Method called by flow to send packet."""
        
        # Debug message
        print
        print self.get_flow_type() + " " + str(self.get_id()) + " sending " + \
              outgoing_packet.packet_type_str() + " packet_" + \
              str(outgoing_packet.get_seq_num()) 

        self.src_host.send_packet(outgoing_packet)
        self.amt_data_sent += outgoing_packet.get_length()

    def end_flow(self):
        """Remove flow from source host's list of flows."""
        # Debug message
        print self.get_flow_type() + " " + str(self.get_id()) + " ending." 

        self.src_host.remove_flow(self.flow_id) 

    def get_flow_type(self):
        """ Helper function to get flow type """
        flow_type = "SendingFlow"
        if "ReceivingFlow" in str(type(self)):
            flow_type = "ReceivingFlow"
        return flow_type

class SendingFlow(Flow):
    """
        A sending flow sends data from the source host to destination host.
        It receives acknowledgment packets.

        Attributes:
               MB_TO_BYTES: Conversion factor. 
               B_TO_Mb: Conversion factor 
               S_TO_MS: Conversion factor.
               MS_TO_S: Conversion factor.
               DATA_PCK_SIZE: Size of data packet in bytes.
    """
    MB_TO_BYTES = 2 ** 20
    B_TO_Mb = 1.0 / (MB_TO_BYTES) * 8
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
                   receive_packet_event:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.
                   received_batch_event:
                       Internal event triggered when ack packets for all outstanding
                       packets hve been received.
                   num_packets_received:
                       Number of packets received since interval start time.
                   amt_data_sent:
                       Number of packets sent since interval start time.
                   amt_data_received:
                       Number of packets received since interval start time.
                   sum_RTT_delay:
                       Sum of round-trip time delays seen for ack packets 
                       received since interval start time.        
                   window_size: Window size for transmission.
                   retransmit_timeout: Timeout (in ms) for retransmission if no
                       ack packet is received.  
                   old_packets: List of packets sent in the previous window.    
                   num_unack_packets: Number of unacknowledged packets.    
                   seq_num: Sequence number of next packet to be sent.  
                   start_num: Sequence number of first data packet in current batch.            
                   ack_dict: Dictionary with keys as sequence numbers of data 
                       packets in current batch and boolean values indicating if 
                       an ack packet has been received for it.   
        """       
        super(SendingFlow, self).__init__(env, flow_id, dest_host_id, src_host)

        self.data_amt = data_amt_MB * SendingFlow.MB_TO_BYTES
        self.start_time = start_time_s * SendingFlow.S_TO_MS
        # Flow has not ended yet.
        self.end_time = None

        # Notification event. 
        self.received_batch_event = env.event()  

        # Default window size and timeout.
        self.window_size = 1
        self.retransmit_timeout = 100
     
        # Intiliaze fields for packet accounting.
        self.old_packets = None
        self.num_unack_packets = 0
        self.seq_num = 1
        self.start_num = 1
        self.ack_dict = {}        
 
        # Initiliaze field for metrics reporting.
        self.sum_RTT_delay = 0

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

    def run(self, env):
        """
            Implements the functionality of a sending flow.
 
            In this implementation, the flow sends window_size number of 
            packets and waits until retransmit_timeout or all ack packets
            are received. If timeout occurs, then all the packets in the
            current batch are resent. 
        """
        # Passivate until start time.
        yield env.timeout(self.start_time)
  
        # Process to handle incoming ack packets.
        env.process(self.monitor_incoming_packets(env))
 
        resend = False 
        while self.data_amt > 0:
            if (resend):
                self.resend_data()
            else:
                self.send_next_data()
 
            # Create new timer event.
            timer = env.timeout(self.retransmit_timeout) 
            yield self.received_batch_event | timer
            
            if (self.received_batch_event.triggered):
                resend = False
                self.received_batch_event = env.event()
                if not timer.triggered: 
                    # This (old) timer should not have any effect.
                    timer.callbacks = None 
            else:
                resend = True

        # All the data has been sent. Send FIN packet.
        fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                               self.dest_host_id, env.now, 
                               self.seq_num)
        self.send_packet(fin_packet)
        
        # Passivate until a FIN packet is received in response.
        yield self.receive_packet_event
        received_packet = self.received_packets.pop()
        
        # Throw error if packet is not FIN packet with correct seq_num.
        assert(received_packet.get_packet_type() == 
               Packet.PacketTypes.fin_packet)
        assert(received_packet.get_seq_num() == self.seq_num) 
               
        # End flow.
        self.end_time = env.now
        self.end_flow()      

    def send_next_data(self):
        """Send next batch of data packets."""
        count = 0
        data_sent = 0
        self.old_packets = []
        self.ack_dict = {}
        self.start_num = self.seq_num
        while (count < self.window_size and data_sent < self.data_amt):
            # Create new packet.
            data_packet = DataPacket(self.src_host_id, self.flow_id, 
                                     self.dest_host_id, self.env.now, 
                                     self.seq_num)
            self.send_packet(data_packet) 
            self.old_packets.append(data_packet)
            self.ack_dict[self.seq_num] = False
            self.seq_num += 1
            count += 1
            data_sent += SendingFlow.DATA_PCK_SIZE 
        
        # Reset counter of unack packets.
        self.num_unack_packets = count   
        
    def resend_data(self):
        """Resend data packets sent in previous window."""
        for i in range(len(self.old_packets)):
            # Update timestamp and send.
            self.old_packets[i].timestamp = self.env.now 
            self.send_packet(self.old_packets[i])

        # Reset ack_dict and counter of unack packets.
        for seq_num in ack_dict.keys():
            self.ack_dict[seq_num] = False
        self.num_unack_packets = len(self.old_packets)           
        
    def monitor_incoming_packets(self, env):
        """Process to handle incoming ack packets."""
        while self.data_amt > 0:
            yield self.receive_packet_event
            received_packet = self.received_packets.pop()
         
            # Throw error if packet not an ack packet.
            assert(received_packet.get_packet_type() == 
                    Packet.PacketTypes.ack_packet)   
            
            rec_seq_num = received_packet.get_seq_num()        
            if (self.ack_dict.has_key(rec_seq_num) and  
                self.ack_dict[rec_seq_num] == False):
                
                self.ack_dict[rec_seq_num] = True
                self.num_unack_packets -= 1 
                
                # Add RTT delay for data_packet.
                self.sum_RTT_delay += (env.now - \
                     self.old_packets[rec_seq_num - self.start_num].get_timestamp())
                           
                # Reset event
                self.receive_packet_event = env.event()
             
            if (self.num_unack_packets == 0):
                self.data_amt -= len(self.old_packets) * SendingFlow.DATA_PCK_SIZE   
                self.received_batch_event.succeed()

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
           us reported to be 0.

           If the flow has not yet started or it has ended in a previous 
           reporting interval, (0, 0, 0) is returned.
        """     
        # Time passed in s.
        time_interval = self.get_reporting_interval()
        assert(time_interval > 0)

        # Calculate send/receive rates (Mbps) and average RTT (in ms).
        flow_send_rate = (self.amt_data_sent * SendingFlow.B_TO_Mb) / time_interval
        flow_receive_rate = (self.amt_data_received * SendingFlow.B_TO_Mb) / time_interval
        
        if (self.num_packets_received > 0):
            flow_avg_RTT = self.sum_RTT_delay / self.num_packets_received
        else:
            flow_avg_RTT = 0

        # Reset counters.
        self.num_packets_received = 0
        self.amt_data_sent = 0
        self.amt_data_received = 0
        self.sum_RTT_delay = 0

        return {'flow_send_rate' : flow_send_rate,
                'flow_receive_rate' : flow_receive_rate,
                'flow_avg_RTT' : flow_avg_RTT,
                'flow_window_size' : self.window_size}
               
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
                       Number of packets sent since intervak start time. Needed
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
                ack_packet = AckPacket(self.src_host_id, self.flow_id, 
                                       self.dest_host_id, env.now, 
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
                                       self.dest_host_id, env.now, 
                                       received_packet.get_seq_num())
                self.send_packet(fin_packet)
                break     
       
        self.end_flow()
