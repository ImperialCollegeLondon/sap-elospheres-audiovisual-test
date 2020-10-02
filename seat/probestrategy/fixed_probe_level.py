from .probe_strategy import ProbeStrategy
import numpy as np


class FixedProbeLevel(ProbeStrategy):
    """
    The probe level does not change. Stopping criterion is the predetermined
    number of trials.
    """
    def __init__(self, level, numTrials):
        self.level = level
        self.numTrials = numTrials
        self.storedResults = []
        self.finished = False

    def storeTrialResult(self, result):
        # print(result)
        self.storedResults.append(result)
        # print(self.storedResults)
        if ( len(self.storedResults) >= self.numTrials ):
            self.finished = True

    def getNextProbeLevel(self):
        return self.level

    def getCurrentEstimate(self):
        return np.mean(np.array(self.storedResults))

    def isFinished(self):
        return self.finished
