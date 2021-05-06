from abc import ABC, abstractmethod
import pandas as pd


class ProbeStrategy(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def store_trial_result(self, result):
        pass

    @abstractmethod
    def get_next_stimulus_id(self):
        pass

    @abstractmethod
    def get_next_probe_level(self):
        pass

    @abstractmethod
    def get_next_probe_level_as_string(self):
        pass

    @abstractmethod
    def get_current_estimate(self):
        pass

    @abstractmethod
    def is_finished(self):
        pass

    def get_trial_data(self):
        """
        Get data describing the latest trial (e.g. for writing to log)
        
        Child classes should override this but functional, non-informative
        implementation given here to speed up development
        Returns
        -------
        DataFrame.
            single row
        """
        return pd.DataFrame([['']], columns=['no_info'])