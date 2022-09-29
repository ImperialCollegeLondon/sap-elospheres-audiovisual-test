from .probe_strategy import ProbeStrategy
import numpy as np
import pandas as pd


class FixedProbeLevel(ProbeStrategy):
    """
    The probe level does not change.
    Stimuli are presented in sequence.
    Stopping criterion is the predetermined number of trials.
    """
    def __init__(self, config):
        self.level = config["initial_probe_level"]
        self.numTrials = config["max_num_trials"]
        self.storedResults = []
        self.next_stimulus_id = 0

    def setup(self, ui="gui"):
        if self.level is None:
            self.level = self.prompt_for_user_input(
                prompt='Enter the probe level [dB] as a float:',
                ui='gui', input_type=float)

    def store_trial_result(self, result):
        # print(result)
        self.storedResults.append(result)
        # print(self.storedResults)
        self.next_stimulus_id += 1

    def get_next_stimulus_id(self):
        return self.next_stimulus_id

    def get_next_probe_level(self):
        return self.level

    def get_next_probe_level_as_string(self):
        return str(self.level)

    def get_current_estimate(self):
        return np.mean(np.array(self.storedResults))

    def is_finished(self):
        if (len(self.storedResults) >= self.numTrials):
            return True
        else:
            return False

    def get_trial_data(self):
        """
        Get the result of the most recent trial
        Returns
        -------
        DataFrame.
            single row with single column called 'result'
        """
        return pd.DataFrame([[self.storedResults[-1]]], columns=['result'])