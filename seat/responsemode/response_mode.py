from abc import ABC, abstractmethod


class ResponseMode(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def show_prompt(self, stimulus_id):
        pass

    @abstractmethod
    def wait(self):
        pass
