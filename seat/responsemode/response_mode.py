from abc import ABC, abstractmethod


class ResponseMode(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def show_prompt(self, stimulus_id):
        pass

    @abstractmethod
    def wait(self):
        pass
    
    @abstractmethod
    def get_trial_data(self):
        pass

    def continue_when_ready(self, message="Press enter when ready..."):
        """
        Parameters
        ----------
        message : STR, optional
            Message to display. The default is "Press enter when ready...".

        Returns
        -------
        Bool.:  Depending on implementation it may be possible to cancel. In 
            this case the return value will be False.

        """
        try:
            input(message)
        except KeyboardInterrupt:
            print('Cancelled by user\n')
            return False
        
        return True