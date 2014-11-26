from packet import Packet
from packet import RoutingUpdatePacket

class Router(object):
    def __init__(self, env, router_id, update_interval):
        """
        Attr:
            env:
                main environment
            id:
                id of router
            links:
                a dict of {link_id: link object}
            host_links:
                a dict of {link_id: host_id}, if the link connects to a host
            routing_table:
                a dict of {node_id: link_id}
            min_dists:
                the min cost from the router to other nodes. 
                a dict of {node_id: dist}
            links_to_dists:
                the min cost from the router using a link to other nodes.
                a dict of {link_id: a dict of {node_id: dist}}
            links_update_timestamp:
                stores the last time a link sends over routingUpdatePacket
                a dict of {link_id: timestamp}
            default_link:
                the default link for the router
            update_interval:
                the update_interval for updating the dynamic routing.
        """
        self.env = env
        self.id = router_id
        self.links = {}
        self.host_links = {}
        
        self.routing_table = {}
        self.min_dists = {}
        self.links_to_dists = {}
        self.links_update_timestamp = {}
        
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
        """ Adding a host to the link. """
        hid = host.get_id()
        lid = host.link.get_id()
        self.host_links[lid] = hid
        self.min_dists[hid] = 0
        self.routing_table[hid] = lid
        self.links_to_dists[lid] = {hid: 0}

    def remove_link(self, link):
        """ Remove a link from the router. """
        if link.get_id() in self.links:
            del self.links[link.get_id()]

    def add_static_routing(self, routing_table, default_link=None):
        self.routing_table = routing_table
        self.default_link = default_link
    
    def process_routing_packet(self, packet):
        """ 
        Processes a routing packet.
        Args:
            packet:
                a routingUpdatePacket
        """
        
        # RoutingUpdatePackt has source of link_id
        lid = packet.src
        
        link = self.links[lid]
        link_cost = link.get_weight()
        link_dists = packet.get_distance_estimates()

        # Updating the distances between the router and other nodes using this
        # specific link. Note we should also add the current link_cost on
        # the link_dist
        self.links_to_dists[lid] = {nid: link_cost + link_dists[nid] for nid in link_dists}
        self.links_update_timestamp[lid] = self.env.now
        self.update_table()
    
    def update_table(self):
        min_dists = {}
        for lid in self.links:
            if lid in self.host_links:
                continue
            elif (lid in self.links_to_dists and
                  self.links_update_timestamp[lid] + 2 * self.update_interval >= self.env.now):
                
                # We will only update with infomation sent within two update_interval time
                cur_dists = self.links_to_dists[lid]
                for nid in cur_dists:
                    if (not nid in min_dists or cur_dists[nid] < min_dists[nid]):
                        min_dists[nid] = cur_dists[nid]
                        self.routing_table[nid] = lid

        # If we changed the min dists, we should broadcast it to neighbors
        change = self.min_dists == min_dists
        self.min_dists = min_dists
        
        if change:
            self.broadcast_dists()
    
    def broadcast_dists(self):
        for link in self.links.values():
            # only broadcast to non-host links
            if not link in self.host_links:
                packet = RoutingUpdatePacket(link.id, -1, -1, self.env.now, 0,
                                             self.min_dists)
                link.enqueue(packet, self.id)
        
    def dynamic_routing(self):
        while True:
            self.update_table()
            yield self.env.timeout(self.update_interval)

    def receive_packet(self, packet):
        """ Receives a packet. """

        print "Router %d receives packet from %d to %d" %(
            self.id, packet.src, packet.dest)
            
        if packet.packet_type == Packet.PacketTypes.routing_update_packet:
            self.process_routing_packet(packet)
        else:
            dest = packet.dest
            if (dest in self.routing_table and
                self.routing_table[dest] is not None):
                print "Routing packet to link %d" %(self.routing_table[dest])
                self.links[self.routing_table[dest]].enqueue(packet, self.id)
            elif self.default_link:
                self.default_link.enqueue(packet, self.id)
