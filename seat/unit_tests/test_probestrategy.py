import numpy as np
from textwrap import dedent
import unittest
from unittest.mock import patch, mock_open

from probestrategy import FixedProbeLevel
from probestrategy import MultipleFixedProbeLevels
from probestrategy import TargetEightyPercent
from probestrategy import TargetFiftyPercent
from probestrategy import TargetTwentyPercent
from probestrategy import DualTargetTwentyEightyPercent
from probestrategy import PsychometricFunction

class TestFixedProbeLevel(unittest.TestCase):
    def test_end_criterion(self):
        """
        Test that it loops the correct number if times
        """
        dummy_data = [[True, False], [False, True], [True, True], [False, False]]
        MAX_NUM_TRIALS = 3
        config = {"initial_probe_level": 0.6,
                  "max_num_trials": MAX_NUM_TRIALS}
        ps = FixedProbeLevel(config)
        counter = 0
        while not ps.is_finished():
            # feed in data
            ps.store_trial_result(dummy_data[counter])
            counter += 1
            
        self.assertEqual(counter, MAX_NUM_TRIALS)



    def test_mean_boolean_lists(self):
        """
        Test that the current estimate is correct
        """
        dummy_data = [[False, False, False, False],
                      [True, True, True, True],
                      [False, False, True, True],
                      [True, True, True, True]]
        cum_mean = [0, 0.5, 0.5, 0.625]
        config = {"initial_probe_level": 0.6,
                  "max_num_trials": len(dummy_data)}
        ps = FixedProbeLevel(config)
        for data, avg in zip(dummy_data, cum_mean):
            # print(data)
            
            # feed in data
            ps.store_trial_result(data)

            # check estimated
            self.assertEqual(ps.get_current_estimate(), avg)


class TestMultipleFixedProbeLevels(unittest.TestCase):

    DATA = dedent("""
            -10.0
            -5.0
            0
            5
            10
            """).strip()
    
    @patch("builtins.open", mock_open(read_data=DATA)) 
    def setUp(self):
        """
        Instantiate the class under test with mocked open and dummy data to external
        file dependency
        """
        self.probe_offsets = np.arange(-10, 10+1, 5, dtype=float) # needs to match DATA
        self.probe_level = 0
        config = {"initial_probe_level": self.probe_level,
                  "max_num_trials": len(self.probe_offsets),
                  "probe_level_variations_file": 'ignored_in_patched_open.csv'}
        self.ps = MultipleFixedProbeLevels(config)
        self.ps.setup()
            
         
                   
    def test_level_sequence_wrt_0(self):
        """
        Test that it loops the correct number if times and gives correct value with
        respect to the defauld probe level of 0
        """

        rng = np.random.default_rng(5387)
        for (i, offset) in enumerate(self.probe_offsets):
            # in the loop shouldn't be finished yet
            self.assertFalse(self.ps.is_finished())
            self.assertEqual(self.ps.get_next_probe_level(), self.probe_level + offset)
            
            # feed in data
            result = rng.choice([False, True], size=(1,5))
            self.ps.store_trial_result(result)

        # should be no more trials left
        self.assertTrue(self.ps.is_finished())

    def test_level_sequence_wrt_10(self):
        """
        Test that it loops the correct number if times and gives correct value with
        respect to the defauld probe level of 0
        """
        self.probe_level = 10
        self.ps.fixed_level = 10.0

        rng = np.random.default_rng(5387)
        for (i,offset) in enumerate(self.probe_offsets):
            # in the loop shouldn't be finished yet
            self.assertFalse(self.ps.is_finished())
            self.assertEqual(self.ps.get_next_probe_level(), self.probe_level + offset)
            
            # feed in data
            result = rng.choice([False, True], size=(1,5))
            self.ps.store_trial_result(result)

        # should be no more trials left
        self.assertTrue(self.ps.is_finished())




class TestTargetEightyPercent(unittest.TestCase):
    def test_step_size_0_correct(self):
        dummy_data = [False, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 4 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 4 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_1_correct(self):
        dummy_data = [True, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 3 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 3 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_2_correct(self):
        dummy_data = [True, True, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 2 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 2 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_3_correct(self):
        dummy_data = [True, True, True, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 1 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_4_correct(self):
        dummy_data = [True, True, True, True, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 0 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 0 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_5_correct(self):
        dummy_data = [True, True, True, True, True]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -1 + initial_probe_level
        ps = TargetEightyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())



class TestTargetTwentyPercent(unittest.TestCase):
    def test_step_size_0_correct(self):
        dummy_data = [False, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 1 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_1_correct(self):
        dummy_data = [True, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 0 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 0 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_2_correct(self):
        dummy_data = [True, True, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -1 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_3_correct(self):
        dummy_data = [True, True, True, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -2 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -2 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_4_correct(self):
        dummy_data = [True, True, True, True, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -3 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -3 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_5_correct(self):
        dummy_data = [True, True, True, True, True]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -4 + initial_probe_level
        ps = TargetTwentyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -4 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())


class TestTargetFiftyPercent(unittest.TestCase):
    def test_step_size_0_correct(self):
        dummy_data = [False, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 3 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 3 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_1_correct(self):
        dummy_data = [True, False, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 2 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 2 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_2_correct(self):
        dummy_data = [True, True, False, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * 1 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * 1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_3_correct(self):
        dummy_data = [True, True, True, False, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -1 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -1 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_4_correct(self):
        dummy_data = [True, True, True, True, False]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -2 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -2 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

    def test_step_size_5_correct(self):
        dummy_data = [True, True, True, True, True]
        initial_probe_level = -5
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": 3}
        correct_result = 1.5 * -3 + initial_probe_level
        ps = TargetFiftyPercent(config)
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())

        correct_result = 1.5 * -3 + correct_result
        ps.store_trial_result(dummy_data)
        self.assertEqual(correct_result, ps.get_next_probe_level())


    def test_convergence(self):
        num_trials = 100
        trials_to_average = 50
        true_threshold = 0
        start_offset_list = [-10, 0, 10]
        true_slope = 0.1
        step_size = 0.1
        acceptable_margin = 10.0
        for start_offset in start_offset_list:
            initial_probe_level = true_threshold + start_offset
            probe_fig_save_path='convergence_step_' + str(step_size) + \
                          '_from_srt_' + str(start_offset) + '.pdf'
            config = {"initial_probe_level": initial_probe_level,
                      "max_num_trials": num_trials,
                      "num_trials_to_average": trials_to_average,
                      "step_size": step_size,
                      "verbosity": 1,
                      "display_plot": False,
                      "save_probe_history_plot": True,
                      "probe_fig_save_path": probe_fig_save_path}
            ps = TargetFiftyPercent(config)
            dummy_listener = PsychometricFunction(threshold_db=true_threshold,
                                                  slope_at_threshold=true_slope)
            while not ps.is_finished():
                probe_level = ps.get_next_probe_level()
                success_vector = dummy_listener.probe_response(probe_level,
                                                               num_responses=5)
                # print(success_vector)
                ps.store_trial_result(success_vector)
            estimated_threshold = ps.get_current_estimate()
            estimation_error = np.abs(estimated_threshold-true_threshold)
            print('Estimation error from srt + ' + str(start_offset) + 
                  ' (db): ' + str(estimation_error))
            self.assertTrue(estimation_error <= acceptable_margin)


class TestDualTargetTwentyEightyPercent(unittest.TestCase):
    def test_convergence(self):
        num_trials = 100
        trials_to_average = 50
        true_threshold = 0
        start_offset_list = [-5, 0, 5]
        true_slope = 0.1
        step_size = 1.5
        acceptable_margin = 10.0
        for start_offset in start_offset_list:
            initial_probe_level = true_threshold + start_offset
            probe_fig_save_path='convergence_step_' + str(step_size) + \
                          '_from_srt_' + str(start_offset) + '.pdf'
            regression_fig_save_path='psychometric_function_step_' + \
                          str(step_size) + \
                          '_from_srt_' + str(start_offset) + '.pdf'              
            config = {"initial_probe_level": initial_probe_level,
                      "max_num_trials": num_trials,
                      "num_trials_to_average": trials_to_average,
                      "step_size": step_size,
                      "verbosity": 0,
                      "display_plot": False,
                      "save_probe_history_plot": True,
                      "probe_fig_save_path": probe_fig_save_path,
                      "save_regression_plot": True,
                      "regression_fig_save_path": regression_fig_save_path}
            ps = DualTargetTwentyEightyPercent(config)
            dummy_listener = PsychometricFunction(threshold_db=true_threshold,
                                                  slope_at_threshold=true_slope)
            while not ps.is_finished():
                probe_level = ps.get_next_probe_level()
                success_vector = dummy_listener.probe_response(probe_level,
                                                               num_responses=5)
                # print(success_vector)
                ps.store_trial_result(success_vector)
            estimated_threshold = ps.get_current_estimate()
            estimation_error = np.abs(estimated_threshold-true_threshold)
            print('Estimation error from srt + ' + str(start_offset) + 
                  ' (db): ' + str(estimation_error))
            self.assertTrue(estimation_error <= acceptable_margin)

    def test_track_assignment(self):
        num_repeats = 1000
        num_trials = 20
        max_run_per_track = 3
        # required parameters with arbitrary values
        initial_probe_level = 0
        
        config = {"initial_probe_level": initial_probe_level,
                  "max_num_trials": num_trials,
                  "max_run_per_track": max_run_per_track}
        
        max_seq_length = np.zeros((num_repeats, 1))
        for i in range(num_repeats):
            ps = DualTargetTwentyEightyPercent(config)
            ta = ps.track_assignment
            
            # find repeating elements - use different approach to that inside 
            # DualTargetTwentyEightyPercent. This may be faster
            # diff: vector of non zero values where theres is a change
            # r_[1,]: prepend non zero value as first element is a change
            # flatnonzero: find indices where there is a change
            # amax(diff: find maximum distance beween changes
            max_seq_length[i,0] = np.amax(np.diff(
                np.flatnonzero(np.r_[1,np.diff(ta)])))
            
            if max_seq_length[i,0]>max_run_per_track:
                print(f'{i} of {num_repeats}: {ta}')
        
        max_all_runs = np.amax(max_seq_length)
        # print(f'maximum sequence lenfth {max_all_runs}')
        
        self.assertTrue(max_all_runs<=max_run_per_track)
        
        
if __name__ == '__main__':
    unittest.main()
