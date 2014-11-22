from packet import RoutingUpdatePacket

class Router(object):
    def __init__(self, env, id, update_interval):
        self.env = env
        self.id = id
        self.links = {}
        self.routing_table = {}
        self.dists = {id: 0}
        self.links_to_dists = {}
        self.default_link = None
        self.update_interval = update_interval
    
        env.process(self.dynamic_routing(env))

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
    
    def update_table(self, packet):
        cur_link = self.links[packet.src]
        cur_cost = self.env.now - packet.timestamp
        new_dists = packet.get_distance_estimates()
        self.links_to_dists[cur_link.id] = {nid: cur_cost + new_dists[nid] for nid in new_dists}
        for nid in new_dists:
            if (not nid in self.dists or
                self.dists[nid] > new_dists[nid] + cur_cost):
                
                self.dists[nid] = new_dists[nid] + cur_cost
                self.routing_table[nid] = cur_link
            elif nid != self.id and cur_link == self.routing_table[nid]:
                self.dists[nid] = new_dists[nid] + cur_cost
                for lid in self.links_to_dists:
                    if nid in self.links_to_dists[lid] and self.links_to_dists[lid][nid] < self.dists[nid]:
                        self.dists[nid] = self.links_to_dists[lid][nid]
                        self.routing_table[nid] = self.links[lid]
    
    def dynamic_routing(self, env):
        while True:
            for link in self.links.values():
                packet = RoutingUpdatePacket(link.id, -1, -1, env.now, 1,
                                             self.dists)
                link.enqueue(packet, self.id)
            yield env.timeout(self.update_interval)

    def receive_packet(self, packet):
        """ Receives a packet. """

        print "Router %d receives packet from %d to %d" %(
            self.id, packet.src, packet.dest)
            
        if packet.packet_type == packet.PacketTypes.routing_update_packet:
            self.update_table(packet)
        else:
            dest = packet.dest
            if (dest in self.routing_table and
                self.routing_table[dest] is not None):
                print "Routing packet to link %d" %(
                    self.routing_table[dest].get_id())
                self.routing_table[dest].enqueue(packet, self.id)
            elif self.default_link:
                self.default_link.enqueue(packet, self.id)
