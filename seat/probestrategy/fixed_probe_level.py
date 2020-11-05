from .probe_strategy import ProbeStrategy
import numpy as np


class FixedProbeLevel(ProbeStrategy):
    """
    The probe level does not change. Stopping criterion is the predetermined
    number of trials.
    """
    def __init__(self, config):
        self.level = config["initial_probe_level"]
        self.numTrials = config["max_num_trials"]
        self.storedResults = []
        self.finished = False

    def store_trial_result(self, result):
        # print(result)
        self.storedResults.append(result)
        # print(self.storedResults)
        if (len(self.storedResults) >= self.numTrials):
            self.finished = True

    def get_next_probe_level(self):
        return self.level

    def get_current_estimate(self):
        return np.mean(np.array(self.storedResults))

    def is_finished(self):
        return self.finished
