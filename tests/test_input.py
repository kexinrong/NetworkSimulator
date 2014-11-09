import sys
sys.path.append('../')
import unittest
from input_network import input_network

class TestInputFunction(unittest.TestCase):
    """Test for input_network function."""
    
    def setUp(self):
        """Set up dictionaries based on test cases 0 - 2."""

        self.CASE_0 = { 
                        "Hosts" : 2, 
                        "Routers" : 0,
                        "Links" : [ [10, 10, 64, ["H", 1], ["H", 2]] ],
                        "Flows" : [ [20, 1.0, 1, 2] ]
                      }
        self.CASE_1 = { 
                        "Hosts" : 2, 
                        "Routers" : 4, 
                        "Links" : [ [12.5, 10, 64, ["H", 1], ["R", 1] ],
                                    [10, 10, 64, ["R", 1], ["R", 2] ],
                                    [10, 10, 64, ["R", 1], ["R", 3] ],
                                    [10, 10, 64, ["R", 2], ["R", 4] ],
                                    [10, 10, 64, ["R", 3], ["R", 4] ],
                                    [12.5, 10, 64, ["R", 4], ["H", 2] ] ],
                        "Flows" : [ [20, 0.5, 1, 2] ]
                      }
        self.CASE_2 = { 
                        "Hosts" : 6, 
                        "Routers" : 4, 
                        "Links" : [ [10, 10, 128, ["R", 1], ["R", 2] ],
                                    [10, 10, 128, ["R", 2], ["R", 3] ],
                                    [10, 10, 128, ["R", 3], ["R", 4] ],
                                    [12.5, 10, 128, ["H", 1], ["R", 1] ],
                                    [12.5, 10, 128, ["H", 2], ["R", 2] ],
                                    [12.5, 10, 128, ["H", 3], ["R", 3] ],
                                    [12.5, 10, 128, ["H", 4], ["R", 4] ],
                                    [12.5, 10, 128, ["H", 5], ["R", 1] ],
                                    [12.5, 10, 128, ["H", 6], ["R", 4] ] ],
                        "Flows" : [ [35, 0.5, 5, 4],
                                    [15, 10, 1, 2],
                                    [30, 20, 3, 6] ]
                      }

    def test_input_network(self):
        """Tests input_network on the three test cases."""
        
        # Check if network_specs dictionary is correct.
        network_specs = input_network("../test_case_0")
        self.assertTrue(cmp(network_specs, self.CASE_0) == 0)
         
        network_specs = input_network("../test_case_1")
        self.assertTrue(cmp(network_specs, self.CASE_1) == 0)

        network_specs = input_network("../test_case_2")
        self.assertTrue(cmp(network_specs, self.CASE_2) == 0)

if __name__ == '__main__':
    unittest.main()
