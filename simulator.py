'''
The main function for the network simulator
'''

import sys, getopt
from env import *

def main(argv):
	input = ''
	output = ''
	duration = 0
	interval = 0	

	try:
		opts, args = getopt.getopt(argv, "hi:o:t:p:", ["ifile=", "ofile=", "total=", "period="])
	except getopt.GetoptError:
		print ('simulator.py -i <intputFile> -o <outputFile> ' 
		       '-t <totalDuration> -p <reportPeriod>')
		sys.exit(2)
	for opt, arg in opts:
		if opt=='-h':
			print 'simulator.py -i <intputFile> -o <outputFile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			input = arg
		elif opt in ("-o", "--ofile"):
			output = arg
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
	mainEnv.start(input, output)	


if __name__ == "__main__":
	main(sys.argv[1:])
