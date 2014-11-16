class Router(object):
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.links = {}
        self.routing_table = {}
        self.default_link = None

    def get_id(self):
        """ Returns host ID."""
        return self.id

    def add_link(self, link):
        """ Adding one link to the router. """
        self.links[link.get_id()] = link

    def add_links(self, links):
        """ Adding a list of links to the router. """
        for link in links:
            self.links[link.get_id()] = link

    def remove_link(self, link):
        """ Remove a link from the router. """
        if link.get_id() in self.links:
            del self.links[link.get_id()]

    def add_static_routing(self, routing_table, default_link=None):
        self.routing_table = routing_table
        self.default_link = default_link

    def receive_packet(self, packet):
        """ Receives a packet. """
        if pack.dest == self.id:
            pass
        else:
            dest = packet.dest
            if (dest in self.routing_table and
                self.routing_table[dest] is not None):
                
                self.routing_table[dest].enqueue(packet, self.id)
            elif self.default_link:
                self.default_link.enqueue(packet, self.id)
