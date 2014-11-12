import json

def input(fname):
    """Reads input json file and returns the network specification as a dictionary. 
       The dictionary format is:
       {
         "Hosts" : Number of hosts, 
         "Routers" : Number of routers,
         "Links" : [ [Link Rate (Mbps), Link Delay (ms), Link Buffer (KB), 
                     ['H' or 'R', id], ['H' or 'R', id] ] ],   
         "Flows" : [ [Data Amt (MB), Flow start (s), Src host id, Dest host id] ]
       }   

       Host IDs range from 1 to Number of Hosts. Similarly for Flow IDs.
       Each link corresponds to a list with the last two entries specifying which 
       hosts ('H') or routers ('R') the link connects. 
    """      
    json_data = open(fname)
    network_specs = json.load(json_data)
    json_data.close()
    return network_specs
