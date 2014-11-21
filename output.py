"""Output module for the network simulator
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class RealTimeGraph:
    ''' Output class that stores data collected by the environment
        and draws real time performance curves 
            duration: 
                user specified duration of the simulation (in ms)
            interval: 
                interval that the environment collects data at (in ms)
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
    MS_TO_S = 1000.0
    # Legends for all subplots
    HOST_FIELDS = ['host_send_rate',
                   'host_receive_rate',
                  ]
                    
    FLOW_FIELDS = ['flow_send_rate',
                   'flow_receive_rate',
                   'flow_avg_RTT',
                  ]
    
    COLORS = 'bgrcmyk'

    LINK_FIELDS = ['packet_loss',
                   'buffer_occupancy',
                   'link_rate',
                  ]

    LEGENDS = HOST_FIELDS + FLOW_FIELDS + LINK_FIELDS

    MAX_PLOTS = len(LEGENDS)

    UNITS = {'host_send_rate': ' (Mbps)',
             'host_receive_rate': ' (Mbps)',
             'flow_send_rate' : ' (Mbps)',
             'flow_receive_rate' : ' (Mbps)',
             'flow_avg_RTT' : ' (ms)',
             'packet_loss' : ' (pkts)',
             'buffer_occupancy' : ' (%)',
             'link_rate' : ' (Mbps)'
            }

    def __init__(self, duration, interval, gtype, num_hosts, num_links, num_flows):
        self.duration = duration / RealTimeGraph.MS_TO_S
        self.interval = interval / RealTimeGraph.MS_TO_S
        self.fig = plt.figure(figsize=(10, 7), dpi=100)
        self.fig.subplots_adjust(hspace=1)
        self.axes = []
        self.data_points = {}
        self.time_series = [0]
        title = 'Network Simulation Plots'
        # Select subgraphs to output 
        if gtype == "host":
            self.legends = RealTimeGraph.HOST_FIELDS
            title += ' (Hosts)'
        elif gtype == "flow":
            self.legends = RealTimeGraph.FLOW_FIELDS
            title += ' (Flows)'
        elif gtype == "link":
            self.legends = RealTimeGraph.LINK_FIELDS
            title += ' (Links)'
        else:
            self.legends = RealTimeGraph.LEGENDS

        self.fig.suptitle(title)

        self.num_plots = len(self.legends)
        for i in range(self.num_plots):
            legend = self.legends[i]
            self.axes.append(
                self.fig.add_subplot(self.num_plots, 1, i + 1))
        
        for i in range(RealTimeGraph.MAX_PLOTS):
            legend = RealTimeGraph.LEGENDS[i]
            self.data_points[legend] = []
            n = 1
            if legend in RealTimeGraph.LINK_FIELDS:
                n = num_links
            elif legend in RealTimeGraph.FLOW_FIELDS:
                n = num_flows
            elif legend in RealTimeGraph.HOST_FIELDS:
                n = num_hosts
            for i in range(n):
                self.data_points[legend].append([0])

    def init_frame(self):
        ''' Function to draw a clear frame '''
        for i in range(self.num_plots):
            self.axes[i].set_ylabel(self.legends[i])
            self.axes[i].set_xlim(0, self.duration)
        self.axes[self.num_plots - 1].set_xlabel('Time (s)')

    def add_data_points(self, data):
        for legend in data:
            for i in range(len(data[legend])):
                self.data_points[legend][i].append(data[legend][i])
        self.time_series.append(
            len(self.data_points[self.legends[0]][0]) * self.interval)
        
    def get_label(self, legend):
        label = 'H'
        if legend in RealTimeGraph.LINK_FIELDS:
            label = 'L'
        elif legend in RealTimeGraph.FLOW_FIELDS:
            label = 'F'
        return label

    def draw(self):
        ''' Helper function to draw the current data points '''
        for i in range(self.num_plots):
            legend = self.legends[i]
            label = self.get_label(legend)
            ax = self.axes[i]
            ax.clear()
            ax.set_ylabel(legend + self.UNITS[legend])
            ax.set_xlim(0, self.duration)
            for i in range(len(self.data_points[legend])):
                ax.plot(self.time_series, self.data_points[legend][i],
                        label = label + str(i + 1))
            ax.legend(bbox_to_anchor=(1.14, 1), loc='best')
        ax.set_xlabel('Time (s)')

    def animate(self, i):
        ''' Animations are made by repeatedly calling this function'''
        self.draw()

    def plot(self):
        ''' Function to run the animation '''
        ani = animation.FuncAnimation(self.fig, self.animate, 
            init_func = self.init_frame, interval = self.INTERVAL)
        plt.show()

    def show(self):
        ''' Function to show the graph '''
        self.draw()
        plt.show()

    def export_to_jpg(self):
        ''' Function to export the plots into a file'''
        self.fig.savefig('performance_curves.jpg', dpi = 500)

    def export_to_file(self):
        ''' Function to raw data points into a file'''
        f = open('raw_data.txt', 'w')
        for i in range(RealTimeGraph.MAX_PLOTS):
            legend = self.LEGENDS[i]
            f.write(legend + '\n')
            for j in range(len(self.data_points[legend])):
                f.write(str(j + 1) + ':' + 
                        str(self.data_points[legend][j]) + '\n')
        f.close()

