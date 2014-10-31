'''
The main function for the network simulator
'''

import sys, getopt
from env import *

def main(argv):
	input = ''
	output = ''
	totalDur = 0
	reportPer = 0	

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
			totalDur = int(arg)
		elif opt in ("-p", "--period"):
			reportPer = int(arg)

	if totalDur <= 0:
		print 'Total duration should be a positive integer'
		sys.exit(2)
	if reportPer <= 0:
		print 'Repositive period should be a positive integer'
		sys.exit(2)
	
	mainEnv = MainEnv()
	mainEnv.start(totalDur, reportPer, input, output)	


if __name__ == "__main__":
	main(sys.argv[1:])
