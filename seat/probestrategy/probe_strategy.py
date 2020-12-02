from abc import ABC, abstractmethod


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
