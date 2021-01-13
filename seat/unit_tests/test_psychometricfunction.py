import unittest
import numpy as np
from probestrategy import PsychometricFunction


class TestPsychometricFunction(unittest.TestCase):
    def test_number_of_elements(self):
        """
        Test that the correct number of intervals are returned
        """
        probe_level_db = 0
        num_response_intervals_set = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        pf = PsychometricFunction()
        for num_response_intervals in num_response_intervals_set:
            # in the loop shouldn't be finished yet
            response = pf.probe_response(probe_level_db,
                                         num_responses=num_response_intervals)

            # check size
            self.assertTrue(len(response) == num_response_intervals)

    def test_return_type(self):
        """
        Test that the returned vector contains only 1s and 0s
        """
        probe_level_db = 0
        num_response_intervals = 100
        pf = PsychometricFunction()
        response = pf.probe_response(probe_level_db,
                                     num_responses=num_response_intervals)
        for interval_response in response:
            self.assertTrue(interval_response in [0, 1])

    def test_function_shape(self):
        # defaults in PsychometricFunction
        slope_at_threshold = 0.1
        threshold_db = 0
        num_response_intervals = 100000  # want a good approximation
        probe_levels = np.linspace(-30, 30, 200)
        allowable_error = 0.01
        pf = PsychometricFunction()

        for probe_level_db in probe_levels:
            p_target = 1/(1 + np.exp(-slope_at_threshold *
                                     (probe_level_db - threshold_db)))
            response = pf.probe_response(probe_level_db,
                                         num_responses=num_response_intervals)
            p_response = np.mean(response)
            # print(str(p_target) + ': ' + str(p_response))
            self.assertTrue(np.abs(p_target-p_response) < allowable_error)


if __name__ == '__main__':
    unittest.main()
