"""Defines the properties and methods of network flow processes."""

from packet import Packet, DataPacket, AckPacket, FINPacket

class Flow(object):
    """
        A flow represents an end-to-end connection. Flows can be of two types:
        receiving and sending flows.  
    """  
    def __init__(self, env, flow_id, src_host, dest_host_id):
        """
            Sets up a flow object. 
 
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       ID of flow.
                   src_host:
                       Host object where the flow starts.
                   dest_host_id:
                       ID of host where flow ends.  
               
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
        self.src_host_id = src_host.get_host_id()
        self.dest_host_id = dest_host_id

        # Set up received_packets buffer. May be useful for congestion control.
        self.received_packets = []

        # Set up flow's notification event
        self.receive_packet = env.event()      

    def get_flow_id(self):
        """Returns flow ID."""   
        return self.flow_id

    def receive_packet(self, incoming_packet):
        """Method called by flow's source host to transmit packet to flow."""     
        # Add packet to flow's received_packets buffer.
        self.received_packets.append(incoming_packet)     

        # Trigger notification event to reactivate flow.
        self.receive_packet.succeed()

    def end_flow(self):
        """Remove flow from source host's list of flows."""
        self.src_host.remove_flow(self.flow_id) 

class SendingFlow(Flow):
    """
        A sending flow sends data from the source host to destination host.
        It receives acknowledgment packets.

        Attributes:
                     MB_TO_BYTES: Conversion factor.  
                     S_TO_MS: Conversion factor.
                     DATA_PCK_SIZE: Size of data packet in bytes.
                     FIN_PCK_SIZE: Size of fin packet in bytes.
    """
    MB_TO_BYTES = 2 ** 20
    S_TO_MS = 1000
    DATA_PCK_SIZE = 1024
    FIN_PCK_SIZE = 64

    def __init__(self, env, flow_id, src_host, dest_host_id, data_amt_MB, start_time_s):
        """
            Sets up a sending flow object.
           
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       Identification number of flow.
                   src_host:
                       Host object in which the flow starts.
                   dest_host_id:
                       ID of host where flow ends. 
                   data_amt_MB:
                       Amount of data to be transferred in MB. Input uses MB.
                   start_time_s:
                       Time (in seconds) after which flow starts transmitting 
                       data. Input uses seconds.
               
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
                   received_packets:
                       List of packets received so far.
                   receive_packet:
                       Internal event triggered when host wants to deliver a 
                       packet to the flow.
        """       
        super(SendingFlow, self).__init__(env, flow_id, src_host, dest_host_id)

        self.data_amt = data_amt_MB * MB_TO_BYTES
        self.start_time = start_time_s * S_TO_MS

        # Add the run generator to the event queue.
        env.process(self.run())

    def run(self):
       """
           Implements the functionality of a sending flow.

           In this implementation, the flow sends a packet, waits for acknowledgment
           and then sends another packet until there is no more data to send. 
           Data transmission gets stuck if an acknowledment is not received.
       """
       # Passivate until start time.
       yield self.env.timeout(self.start_time)

       seq_num = 1
       while self.data_amt > 0:
           # Create new packet.
           data_packet = DataPacket(self.src_host_id, self.flow_id, 
                                    self.dest_host_id, self.env.now, 
                                    DATA_PCK_SIZE, seq_num)
  
           # Call host function to send packet.  
           self.src_host.send_packet(data_packet)

           # Passivate until an ack packet is received.   
           yield self.receive_packet 
           received_packet = self.received_packets[-1]
           
           # Throw an error if received packet is not an ack packet.
           assert(received_packet.get_packet_type() == 
                  Packet.PacketTypes.acknowledgement_packet)           

           # Check if received ack packet has correct seq_num.  
           if (received_packet.get_sequence_number() == seq_num):
               # Update data_amt and seq_num.
               self.data_amt -= DATA_PCK_SIZE
               seq_num += 1

           # Reset event
           self.receive_packet = self.env.event()
       
       # All the data has been sent. Send FIN packet.
       fin_packet = FINPacket(self.src_host_id, self.flow_id, 
                              self.dest_host_id, self.env.now, 
                              FIN_PCK_SIZE, seq_num)
       self.src_host.send_packet(fin_packet) 
       self.end_flow()      

class ReceivingFlow(Flow):
    """
        A receiving flow receives data packets and sends acknowledgments.

        Attributes:
                     ACK_PCK_SIZE: Size of ack packet in bytes. 
    """
    ACK_PCK_SIZE = 64

    def __init__(self, env, flow_id, hosts):
        """
            Sets up a receiving flow object.
           
            Args:
                   env: 
                       SimPy environment in which flow resides.
                   flow_id:
                       Identification number of flow (same as corresponding 
                       sending flow).
                   src_host:
                       Host object in which the flow starts.
                   dest_host_id:
                       ID of host where flow ends. 
               
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
        super(ReceivingFlow, self).__init__(env, flow_id, hosts)

        # Add the run generator to the event queue.
        self.env.process(self.run())

    def run(self):
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
                                      self.dest_host_id, self.env.now, 
                                      ACK_PCK_SIZE, received_packet.get_sequence_number())
     
               # Call host function to send packet.  
               self.src_host.send_packet(ack_packet)

               # Reset event.
               self.receive_packet = self.env.event()

           else: 
               # Throw error if packet is not a FIN_packet
               assert(received_packet.get_packet_type() == 
                      Packet.PacketTypes.fin_packet)
               # FIN_packet received. Stop running.
               break     
       
       self.end_flow()
