"""Output module for the network simulator
"""
import matplotlib.pyplot as plt

class RealTimeGraph:
	''' Output class that stores data collected by the environment
	    and draws real time performance curves 

		    duration: 
		    	user specified duration of the simulation (in sec)
		    interval: 
		    	interval that the environment collects data at (in sec)
		    fig: 
		    	figure object
		    axes:
		    	list of subplots
		    data_points:
		    	value of each subplot
		    time_series: 
		    	x coordinates of all data points
	'''

	# Interval (in ms) at which the real time animation 
	# refreshes the frame
	INTERVAL = 1000 
	# Legends for all subplots
	LEGENDS = ['link rate', 'buffer occupancy', 'packet loss', 
		'flow rate', 'window size', 'packet delay']
	# Number of subplotss
	NUM_PLOTS = len(LEGENDS)

	def __init__(self, duration, interval):
		self.duration = duration
		self.interval = interval
		self.fig = plt.figure()
		self.fig.subplots_adjust(hspace=0.6)
		self.axes = []
		self.data_points = []
		self.time_series = [0]
		for i in range(self.NUM_PLOTS):
			self.axes.append(
				self.fig.add_subplot(self.NUM_PLOTS, 1, i + 1))
			self.data_points.append([0])

	def init_frame(self):
		''' Function to draw a clear frame '''
		for i in range(self.NUM_PLOTS):
			self.axes[i].set_ylabel(self.LEGENDS[i])
			self.axes[i].set_xlim(0, self.duration)
		self.axes[self.NUM_PLOTS - 1].set_xlabel('Time (s)')

	def add_data_points(self, data):
		for i in range(self.NUM_PLOTS):
			self.data_points[i].append(data[i])
		self.time_series.append(
			len(self.data_points[0]) * self.interval)
		
	def animate(self, i):
		''' Animations are made by repeatedly calling this function'''
		for i in range(self.NUM_PLOTS):
			ax = self.axes[i]
			ax.clear()
			ax.set_ylabel(self.LEGENDS[i])
			ax.set_xlim(0, self.duration)
			ax.plot(self.time_series, self.data_points[i])
		ax.set_xlabel('Time (s)')

	def export_to_jpg(self):
		''' Function to export the plots into a file'''
		self.fig.savefig('performance_curves.jpg', dpi = 500)

		



