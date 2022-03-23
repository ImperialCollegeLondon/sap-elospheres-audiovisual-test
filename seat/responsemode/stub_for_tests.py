from .response_mode import ResponseMode
import pandas as pd


class AlwaysCorrect(ResponseMode):
    """Response to every trial is True"""

    def __init__(self, config):
        # pprint.pprint(config)
        pass

    def show_prompt(self, stimulus_id):
        print(f'ResponseMode.show_prompt() called for simulus_id {stimulus_id}')

    def wait(self):
        return True
    
    def get_trial_data(self):
        return pd.DataFrame([[True]],
                            columns = ['correct_response'])

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
        print(f'{message}')
        return True
        
        
class FailsOnWait(ResponseMode):
    """Response to every trial is an Exception"""

    def __init__(self, config):
        # pprint.pprint(config)
        pass

    def show_prompt(self, stimulus_id):
        print(f'ResponseMode.show_prompt() called for simulus_id {stimulus_id}')

    def wait(self):
        if True:
            raise RuntimeError('Exception was raised intentionally by FailsOnWait test stub.')
    
    def get_trial_data(self):
        return pd.DataFrame([[True]],
                            columns = ['correct_response'])

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
        print(f'{message}')
        return True
