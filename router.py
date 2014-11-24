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
        DYNAMIC_ROUTING_INTERVAL after for 0.1s per iteration. All but the
        RoutingUpdatePackets are dropped at the start of the simulation until
        the routers have settled on a routing table.
        
        Because the network objects do not have IP addresses, routing tables are
        a dictionary with keys being all the host ID's and values being the
        corresponding link to forward.
    """
    
    # Interval between dynamic routing sessions in ms.
    DYNAMIC_ROUTING_INTERVAL = 4000
    # Time for each dynamic routing session in ms.
    DYNAMIC_ROUTING_TIME = 100
    
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
                    routing_table:
                        Dictionary with keys as destination host_ids and values
                        as corresponding link_ids to forward packet.
                    dynamic_routing:
                        Boolean value stating whether router is currently
                        engaged in dynamic routing.
                    dist_estimates:
                        Dictionary with keys as destination host_ids and values
                        as propagation delay to that host. Updated during
                        dynamic routing iterations.
                    new_routing_table:
                        Routing table with keys as destination host_ids and
                        values as corresponding links to forward packet. Built
                        up during dynamic routing iterations.
        """
        
        # Current router parameters.
        self.env = env
        self.router_id = router_id
        self.links = {}
        self.routing_table = {}

        # Router parameters updated during dynamic routing.
        self.dynamic_routing = False
        self.dist_estimates = {}
        self.new_routing_table = {}
        
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

        # Drop packet if not currently in dynamic routing phase.
        if not self.dynamic_routing:
            return
        
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
                self.new_routing_table[host_id] = link_id
        
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
        DYNAMIC_ROUTING_INTERVAL in the simulation for DYNAMIC_ROUTING_TIME per
        iteration."""
        while True:
            # Allow RoutingUpdatePackets to be received and handled.
            dynamic_routing = True
            
            # Broadcast current distance estimates.
            broadcast_dist_estimates()
            
            # Allow RoutingUpdatePackets to be received and handled for the
            # next DYNAMIC_ROUTING_TIME ms.
            yield(env.timeout(self.DYNAMIC_ROUTING_TIME))
            
            # Dynamic routing iteration completed. Prevent further handling of
            # RoutingUpdatePackets.
            dynamic_routing = False
            
            # Update routing table based on new distance estimates.
            update_routing_table()
            
            # Wait for another DYNAMIC_ROUTING_INTERVAL ms for the next dynamic
            # routing iteration.
            yield(env.timeout(self.DYNAMIC_ROUTING_INTERVAL))
            
    def update_routing_table(self):
        """Updates routing table and resets parameters for next dynamic routing
        phase."""
        self.routing_table = self.new_routing_table
        
        self.dist_estimates = {}
        self.new_routing_table = {}
