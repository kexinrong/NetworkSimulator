'''
The main function for the network simulator for command line
'''

import sys, getopt
from env import MainEnv

S_TO_MS = 1000

def main(argv):
    """ Command line for running the simulator.
        Args:
            -i:
                input file name
            -t:
                an int, total duration for the network
            -p:
                an int, the report period for collecting stats
    """

    input = ''
    duration = 0
    interval = 0
    updateInterval = .1

    try:
        opts, args = getopt.getopt(argv, "hi:o:t:p:r:d:g:",
                                   ["ifile=", "ofile=",
                                    "total=", "period=",
                                    "update=", "delay="
                                    "graph="])
    except getopt.GetoptError:
        print ('simulator.py '
               '-i <intputFile>'
		       '-t <totalDuration> '
               '-p <reportPeriod>'
               '-r <routingUpdatePeriod>'
               '-g <outputGraph>')
        sys.exit(2)
    for opt, arg in opts:
        # Show everything by default
        graph_type = None
        if opt == '-h':
            print ('simulator.py -i <intputFile> -t <totalDuration> '
                   '-p <reportPeriod> -r <routingUpdatePeriod> '
                   '-d <delayForFlows> -g <outputGraph:id1,id2>' )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            ifile = arg
        elif opt in ("-t", "--total"):
            duration = int(arg)
        elif opt in ("-p", "--period"):
            interval = float(arg)
        elif opt in ("-g", "--graph"):
            args = arg.split(':')
            ids = []
            if len(args) > 1:
                ids = [int(n) for n in args[1].split(',')]
            graph_type = (args[0], ids)
        elif opt in ("-d", "--delay"):
            delayForFlows = float(arg)
        elif opt in ("-r", "--update"):
            updateInterval = float(arg)

    if duration <= 0:
        print 'Total duration should be a positive int'
        sys.exit(2)
    if interval <= 0:
        print 'Interval for data collection should be a positive int'
        sys.exit(2)

    mainEnv = MainEnv(duration * S_TO_MS, interval * S_TO_MS,
                      updateInterval * S_TO_MS, graph_type)
    mainEnv.start(ifile)

if __name__ == "__main__":
    main(sys.argv[1:])
