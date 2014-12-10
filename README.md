NetworkSimulator
================

Network simulator project for CS/EE 143 by Taokun Zheng, Kexin Rong, Aman Agrawal, Aditya Bhagavathi

The simulator takes several arguments:
- -t: total simulation time (in seconds)
- -p: data collecting interval (in seconds)
- -i: input file (test_case_0, test_case_1, test_case_2)
- -g: metrics to plot (link, flow, host, link:1,2 etc.)
- -r: dynamic routing update interval (in seconds)

Example run:
+ python simulator.py -t 40 -p 0.5 -r 5 -i test_case_1 -g link:1,2
+ python simulator.py -t 50 -p 0.5 -i test_case_2 -g flow

The congestion control algorithms for each flow can be specificied in the input files ("FAST" for FAST TCP, and "Tahoe" for TCP Tahoe)

Metrics specified by the -g argument are presented as a real time performance graph. All simulation data will be saved in a raw data file in the 'results' folder when the simulation is over.
