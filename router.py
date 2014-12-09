from packet import Packet, RoutingUpdatePacket
import random

class Router(object):
    def __init__(self, env, router_id, update_interval):
        """
        Attributes:
            env:
                main environment
            router_id:
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
        
        self.update_interval = update_interval
    
        env.process(self.dynamic_routing(self.env))

    def get_id(self):
        """Returns host ID."""
        return self.id

    def add_link(self, link):
        """Adding one link to the router. """
        self.links[link.get_id()] = link
        self.links_update_timestamp[link.get_id()] = None
        
    def add_host(self, host):
        """Adding a host to the link. """
        hid = host.get_id()
        lid = host.link.get_id()
        self.host_links[lid] = hid
        self.min_dists[hid] = 0
        self.routing_table[hid] = lid
        self.links_to_dists[lid] = {hid: 0}

    def remove_link(self, link_id):
        """Remove a link from the router. """
        if link_id in self.links:
            del self.links[link_id]

    def add_static_routing(self, routing_table):
        """Inserts environment-configured routing table. Not currently
        supported due to dynamic programming."""
        self.routing_table = routing_table
    
    def process_routing_packet(self, packet):
        """Processes a routing packet.
        Args:
            packet:
                a RoutingUpdatePacket
        """
        
        # RoutingUpdatePackt has source of link_id
        lid = packet.get_source()
        
        link = self.links[lid]
        link_cost = link.get_weight()
        link_dists = packet.get_distance_estimates()

        # Updating the distances between the router and other nodes using this
        # specific link. Also add the current link_cost on the link_dist.
        self.links_to_dists[lid] = {nid: link_cost + link_dists[nid] 
                                    for nid in link_dists}
        self.links_update_timestamp[lid] = self.env.now
        self.update_table()
    
    def update_table(self):
        """Refreshes routing table based on information in links_to_dists.
        Broadcasts routing information if min_dists changes."""
        
        min_dists = {}
        for lid in self.links:
            # Set dist to host as 0 and lid as forwarding link.
            if lid in self.host_links:
                min_dists[self.host_links[lid]] = 0
                self.routing_table[self.host_links[lid]] = lid
                
            # Only update with infomation sent within two update_interval times.
            elif ((lid in self.links_to_dists) and
                  (self.links_update_timestamp[lid] + 2 * self.update_interval 
                   >= self.env.now)):                
                cur_dists = self.links_to_dists[lid]
                for nid in cur_dists:
                    if (not nid in min_dists or cur_dists[nid] < min_dists[nid]):
                        min_dists[nid] = cur_dists[nid]
                        self.routing_table[nid] = lid
        
        change = self.min_dists != min_dists
        self.min_dists = min_dists
        
        # Broadcast to neighbors if min_dists has changed.
        if change:
            # Broadcast every part to let routing converge at first
            if self.env.now < 500:
                self.broadcast_dists()
            # Broadcast 1/10 of the packets to avoid overflowing the links
            # in the later stage
            elif random.randint(0, 10) == 1:
                self.broadcast_dists()
    
    def broadcast_dists(self):
        """Broadcasts min_dists to all adjacent non-host devices."""
        for lid in self.links:
            # Only broadcast to non-host links
            if not lid in self.host_links:
                packet = RoutingUpdatePacket(lid, -1, -1, self.env.now, 0,
                                             self.min_dists)
                self.links[lid].enqueue(packet, self.id)
        
    def dynamic_routing(self, env):
        """Initializes dynamic routing after every update_interval time."""
        while True:
            self.broadcast_dists()
            yield env.timeout(self.update_interval)
            self.update_table()

    def receive_packet(self, packet):
        """ Receives a packet. """
        
        # Process RoutingUpdatePackets.
        if packet.get_packet_type() == Packet.PacketTypes.routing_update_packet:
            self.process_routing_packet(packet)
        
        # Immediately forward all other packets.
        else:
            dest = packet.get_destination()
            if (dest in self.routing_table and
                self.routing_table[dest] is not None):
                self.links[self.routing_table[dest]].enqueue(packet, self.id)
