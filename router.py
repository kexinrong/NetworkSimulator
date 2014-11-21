"""Defines the properties and methods of router processes."""

class Router(object):
    """
        A router instantaneously forwards packets from one link to another based
        on its routing table. Dynamic routing is performed using the Bellman-
        Ford algorithm with distance vectors. Hosts are responsible for
        responding to RoutingUpdatePackets with a singleton zero distance
        estimate to themselves.
        
        Dynamic routing occurs at the start of the simulation and every
        DYNAMIC_ROUTING_PERIOD after for 0.1s per iteration. All but the
        RoutingUpdatePackets are dropped at the start of the simulation until
        the routers have settled on a routing table.
        
        Because the network objects do not have IP addresses, routing tables are
        a dictionary with keys being all the host ID's and values being the
        corresponding link to forward.
    """
    
    # Interval between dynamic routing sessions in ms.
    DYNAMIC_ROUTING_PERIOD = 5000
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
                        as corresponding links to forward packet.
        """
        
        self.env = env
        self.router_id = router_id
        self.links = {}
        self.routing_table = {}

    def get_id(self):
        """ Returns router ID."""
        return self.router_id

    def add_links(self, links):
        """ Adds a list of links to the router."""
        for link in links:
            self.links[link.get_id()] = link

    def remove_link(self, link_id):
        """ Remove a link from the router."""
        if link_id() in self.links:
            del self.links[link_id()]

    def add_static_routing(self, routing_table):
        self.routing_table = routing_table

    def receive_packet(self, packet):
        """ Receives a packet. """

        # Debug statement.
        print "Router %d receives packet from %d to %d" \
              % (self.id, packet.src, packet.dest)

        dest = packet.get_destination()
        if (dest in self.routing_table and
            self.routing_table[dest] is not None):
            # Debug statement.
            print "Routing packet to link %d" \
                  %(self.routing_table[dest].get_id())
            # Forward packet to corresponding link.
            self.routing_table[dest].enqueue(packet, self.get_id())
