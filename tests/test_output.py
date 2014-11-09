import sys
sys.path.append('../')
from output import RealTimeGraph
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import threading
import random

DURATION = 20
INTERVAL = 0.5
graph = RealTimeGraph(DURATION, INTERVAL)

def collect_report():
	''' Function that periodically feeds new data points 
	    to RealTimeGraph '''
	datapoints = []
	for i in range(int(DURATION / INTERVAL)):
		datapoints = []
		for j in range(graph.NUM_PLOTS):
			datapoints.append(random.randint(0, 20))	
		graph.add_data_points(datapoints)		
		time.sleep(INTERVAL)

if __name__ == '__main__':
	tr = threading.Thread(target=collect_report)
	# Start background thread
	tr.start()
	ani = animation.FuncAnimation(graph.fig, graph.animate, 
		init_func = graph.init_frame, interval = graph.INTERVAL)
	plt.show()
	# Export figure
	graph.export_to_jpg()