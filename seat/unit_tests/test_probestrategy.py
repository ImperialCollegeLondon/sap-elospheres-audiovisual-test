import unittest

from probestrategy import FixedProbeLevel


class TestFixedProbeLevel(unittest.TestCase):
    def test_end_criterion(self):
        """
        Test that it loops the correct number if times
        """
        dummy_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        config = {"initial_probe_level": 0.6,
                  "max_num_trials": len(dummy_data)}
        ps = FixedProbeLevel(config)
        for data in dummy_data:
            # in the loop shouldn't be finished yet
            self.assertFalse(ps.is_finished())

            # feed in data
            ps.store_trial_result(data)

        #
        self.assertTrue(ps.is_finished())

    def test_mean(self):
        """
        Test that the current estimate is correct
        """
        dummy_data = [10, 10, 40, 10]
        cum_mean = [10, 10, 20, 70/4]
        config = {"initial_probe_level": 0.6,
                  "max_num_trials": len(dummy_data)}
        ps = FixedProbeLevel(config)
        for data, avg in zip(dummy_data, cum_mean):

            # feed in data
            ps.store_trial_result(data)

            # check estimated
            self.assertEqual(ps.get_current_estimate(), avg)


if __name__ == '__main__':
    unittest.main()
