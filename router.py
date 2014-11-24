from packet import RoutingUpdatePacket

class Router(object):
    def __init__(self, env, id, update_interval):
        self.env = env
        self.id = id
        self.links = {}
        self.host_links = {}
        
        self.routing_table = {}
        self.min_dists = {id: 0}
        self.links_to_dists = {}
        self.links_update_timestamp = {}
        self.last_update_time = 0
        
        self.default_link = None
        self.update_interval = update_interval
    
        env.process(self.dynamic_routing())

    def get_id(self):
        """ Returns host ID."""
        return self.id

    def add_link(self, link):
        """ Adding one link to the router. """
        self.links[link.get_id()] = link
        self.links_update_timestamp[link.get_id()] = None
    
    def add_host(self, host):
        hid = host.get_id()
        self.host_links[host.link] = host
        self.min_dists[hid] = 0
        self.routing_table[hid] = host.link
        self.links_to_dists[host.link.get_id()] = {hid: 0}

    def remove_link(self, link):
        """ Remove a link from the router. """
        if link.get_id() in self.links:
            del self.links[link.get_id()]

    def add_static_routing(self, routing_table, default_link=None):
        self.routing_table = routing_table
        self.default_link = default_link
    
    def process_routing_packet(self, packet):
        """with open(self.env.rfile, 'a') as fout:
            fout.write('Time: %f\n' % self.env.now)
            fout.write('Router %d receives packet from link %d\n' % (self.id, packet.src))"""
        
        lid = packet.src
        
        link = self.links[lid]
        link_cost = self.env.now - packet.timestamp
        link_dists = packet.get_distance_estimates()

        self.links_to_dists[lid] = {nid: link_cost + link_dists[nid] for nid in link_dists}
        self.links_update_timestamp[lid] = self.env.now
        self.update_table()
    
    def update_table(self):
        routing_table = {}
        min_dists = {self.id: 0}
        for lid in self.links:
            link = self.links[lid]
            if link in self.host_links:
                hid = self.host_links[link].get_id()
                min_dists[hid] = 0
                routing_table[hid] = link
            elif (lid in self.links_to_dists and
                  self.links_update_timestamp[lid] + self.update_interval >= self.env.now):
                cur_dists = self.links_to_dists[lid]
                for nid in cur_dists:
                    if (not nid in min_dists or cur_dists[nid] < min_dists[nid]):
                        min_dists[nid] = cur_dists[nid]
                        routing_table[nid] = link
        self.min_dists = min_dists
        self.routing_table = routing_table
        self.last_update_time = self.env.now
        
        if self.id == 2:
            with open(self.env.rfile, 'a') as fout:
                fout.write('Time: %f\n' % self.env.now)
                fout.write('Router %d updating routing table\n' % (self.id))
                fout.write(str(self.min_dists) + '\n')
                fout.write(str({nid: self.routing_table[nid].get_id() for nid in self.routing_table}) + '\n\n')
    
    def dynamic_routing(self):
        while True:
            for link in self.links.values():
                if not link in self.host_links:
                    packet = RoutingUpdatePacket(link.id, -1, -1, self.env.now, 0,
                                                 self.min_dists)
                    link.enqueue(packet, self.id)
            
            if (self.env.now - self.last_update_time > self.update_interval):
                self.update_table()
            
            yield self.env.timeout(self.update_interval)

    def receive_packet(self, packet):
        """ Receives a packet. """

        print "Router %d receives packet from %d to %d" %(
            self.id, packet.src, packet.dest)
            
        if packet.packet_type == packet.PacketTypes.routing_update_packet:
            self.process_routing_packet(packet)
        else:
            dest = packet.dest
            if (dest in self.routing_table and
                self.routing_table[dest] is not None):
                print "Routing packet to link %d" %(
                    self.routing_table[dest].get_id())
                self.routing_table[dest].enqueue(packet, self.id)
            elif self.default_link:
                self.default_link.enqueue(packet, self.id)
