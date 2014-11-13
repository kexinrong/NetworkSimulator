import sys
sys.path.append('../')
from output import RealTimeGraph
import time
import threading
import random

DURATION = 10000
INTERVAL = 500
graph = RealTimeGraph(DURATION, INTERVAL, 1, 3, 1)

def collect_report():
    ''' Function that periodically feeds new data points 
        to RealTimeGraph '''
    for i in range(int(DURATION / INTERVAL)):
        datapoints = {}
        for j in range(graph.num_plots):
            legend = graph.legends[j]
            if 'flow' not in legend and 'host' not in legend:
                datapoints[legend] = [random.randint(0, 20), 
                                      random.randint(0, 20), 
                                      random.randint(0, 20)]
            else:
                datapoints[legend] = [random.randint(0, 20)]
        graph.add_data_points(datapoints)       
        time.sleep(INTERVAL / 1000.0)

if __name__ == '__main__':
    tr = threading.Thread(target=collect_report)
    # Start background thread
    tr.start()
    # Plot figure
    graph.plot()
    # Export figure
    graph.export_to_jpg()
    # Export to file
    graph.export_to_file()