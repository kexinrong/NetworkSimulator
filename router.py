"""Defines the properties and methods of router processes."""

from packet import RoutingUpdatePacket

class Router(object):
    """
        A router instantaneously forwards packets from one link to another based
        on its routing table. Dynamic routing is performed using the Bellman-
        Ford algorithm with distance vectors. Hosts are responsible for
        responding to RoutingUpdatePackets with a singleton zero distance
        estimate to themselves.
        
        Dynamic routing occurs at the start of the simulation and every
        DYNAMIC_ROUTING_INTERVAL after.
        
        Because the network objects do not have IP addresses, routing tables are
        a dictionary with keys being all the host ID's and values being the
        corresponding link to forward.
    """
    
    # Interval between dynamic routing sessions in ms.
    DYNAMIC_ROUTING_INTERVAL = 5000
    
    def __init__(self, env, router_id):
        """
            Sets up a network router object.
            
            Args:
                    env:
                        SimPy environment in which router resides.
                    router_id:
                        Identification number of router.
                        
            Attributes:
                    links:
                        Dictionary of links (keys are link_ids, values are link
                        objects) connected to router.
                    dist_estimates:
                        Dictionary with keys as destination host_ids and values
                        as propagation delay to that host. Updated during
                        dynamic routing iterations.
                    routing_table:
                        Dictionary with keys as destination host_ids and values
                        as corresponding link_ids to forward packet.
        """
        
        # Current router parameters.
        self.env = env
        self.router_id = router_id
        self.links = {}
        self.dist_estimates = {}
        self.routing_table = {}
        
        # Dynamic routing process.
        self.env.process(self.dynamic_routing(self.env))

    def get_id(self):
        """Returns router ID."""
        return self.router_id

    def add_links(self, links):
        """Adds a list of links to the router."""
        for link in links:
            self.links[link.get_id()] = link

    def remove_link(self, link_id):
        """Remove a link from the router."""
        if link_id() in self.links:
            del self.links[link_id()]

    def receive_packet(self, packet):
        """Receives a packet. Processes it if it is a RoutingUpdatePacket and
        otherwise forwards immediately."""

        # Debug statement.
        print "Router %d receives packet from %d to %d" \
              % (self.router_id, packet.get_source(), packet.get_destination())
        
        # Process RoutingUpdatePackets.
        if (packet.get_packet_type() ==
            Packet.PacketTypes.routing_update_packet):
            process_routing_packet(packet)

        # Immediately forward other packets.
        else:
            dest = packet.get_destination()
            if dest in self.routing_table:
                forwarding_link_id = self.routing_table[dest]
                
                # Debug statement.
                print "Routing packet to link %d" %(forwarding_link_id)
                
                # Forward packet to corresponding link.
                self.links[forwarding_link_id].enqueue(packet, self.get_id())
            
    def process_routing_packet(self, packet):
        """Handles a RoutingUpdatePacket. Updates distance estimates and new
        routing table and broadcasts new information."""
        
        # Boolean for whether packet provides new information.
        new_info = False
        
        # Link through which packet arrived (provided in source field).
        link_id = packet.get_source()
        link_weight = env.now - packet.get_timestamp()
        
        for host_id, delay in packet.get_dist_estimates().iteritems():
            # Add host_id to dist_estimates and new_routing_table if not
            # already present or shorter distance found.
            if (host_id not in self.dist_estimates) or \
               (delay + link_weight < self.dist_estimates[host_id]):
                new_info = True
                self.dist_estimates[host_id] = delay + link_weight
                self.routing_table[host_id] = link_id
        
        # Broadcast new information.
        if new_info:
            broadcast_dist_estimates()

    def broadcast_dist_estimates(self):
        """Broadcasts current distance estimates."""
        for link in self.links.itervalues():
            
            # Create a RoutingUpdatePacket containing current distance
            # distance estimates with link ID in source field.
            routing_update_packet = RoutingUpdatePacket(link.get_id(), -1, -1,
                self.env.now, 0, self.dist_estimates)
            
            link.enqueue(routing_update_packet, self.router_id)

    def dynamic_routing(self, env):
        """Process for scheduling dynamic routing to occur every
        DYNAMIC_ROUTING_INTERVAL in the simulation."""
        while True:
            # Broadcast current distance estimates.
            broadcast_dist_estimates()
            
            # Wait for another DYNAMIC_ROUTING_INTERVAL ms before instigating
            # new dynamic routing phase.
            yield(env.timeout(self.DYNAMIC_ROUTING_INTERVAL))
