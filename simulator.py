'''
The main function for the network simulator for command line
'''

import sys, getopt
from env import MainEnv

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

    try:
        opts, args = getopt.getopt(argv, "hi:o:t:p:",
                                   ["ifile=", "ofile=",
                                    "total=", "period="])
    except getopt.GetoptError:
        print ('simulator.py '
               '-i <intputFile>'
		       '-t <totalDuration> '
               '-p <reportPeriod>')
        sys.exit(2)
    for opt, arg in opts:
        if opt=='-h':
            print ('simulator.py -i <intputFile> -t <totalDuration> '
                   '-p <reportPeriod>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            ifile = arg
        elif opt in ("-t", "--total"):
            duration = int(arg)
        elif opt in ("-p", "--period"):
            interval = int(arg)

    if duration <= 0:
        print 'Total duration should be a positive int'
        sys.exit(2)
    if interval <= 0:
        print 'Interval for data collection should be a positive int'
        sys.exit(2)

    mainEnv = MainEnv(duration, interval)
    mainEnv.start(ifile)

if __name__ == "__main__":
    main(sys.argv[1:])
