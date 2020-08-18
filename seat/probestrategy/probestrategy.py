from abc import ABC, abstractmethod
import numpy as np

class ProbeStrategy(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def storeTrialResult(self, result):
        pass

    @abstractmethod        
    def getNextProbeLevel(self):
        pass
        
    @abstractmethod
    def getCurrentEstimate(self):
        pass
    
    @abstractmethod
    def isFinished(self):
        pass
        
        
