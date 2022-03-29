from enum import Enum
from abc import ABC, abstractmethod
from pandas import DataFrame


class AVRCState(Enum):
    """Enumerate states"""
    INIT = 0
    CONFIGURED = 1
    READY_TO_START = 2
    ACTIVE = 3
    TERMINATED = 4


class AVRendererControl(ABC):
    """Abstract base class to define the interface"""
    def __init__(self):
        self.probe_level = None
        self.state = AVRCState.INIT

    def is_configured(self):
        return self.is_configured

    @abstractmethod
    def load_config(self, config):
        """
        Call `load_config(config)` to pass the required settings, overriding
        any defaults which have been set

        Note: calling load_config() may be optional, depending on the
        implementation
        """
        pass

    def setup(self):
        """
        Call `setup()` after `load_config()` to get everything prepared
        """
        pass

    @abstractmethod
    def start_scene(self):
        """
        The audio visual scene will start including any continuous background
        material (noise/maskers) and/or any idle material which is active only
        between trials
        """
        pass

    @abstractmethod
    def set_probe_level(self, probe_level):
        """
        Adjust the independent parameter which is being controlled

        Depending on the implementation probe_level could be anything so
        subclasses must implement and do all validation themselves
        """
        pass

    @abstractmethod
    def present_trial(self, stimulus_id):
        """Trigger trial using stimulus given by stimulus_id (0-based)"""
        pass

    def present_preparatory_content(self):
        """
        Opportunity to show source content after scene starts before first trial
        """
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
        return DataFrame([['']], columns=['no_info'])
