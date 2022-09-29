from abc import ABC, abstractmethod
import pandas as pd
import PySimpleGUI as sg
import click


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

    def setup(self):
        """
        Provide a hook to allow for any additional setup which may be required
        
        """
        pass

        
    def prompt_for_user_input(self, ui="gui", prompt="Enter information:", input_type=float):
        
        ui_allowed_values=["gui", "cli"]
        if ui not in ui_allowed_values:
            raise ValueError(f'ProbeStrategy.prompt_for_user_input(): Expect ui to be one of {ui_allowed_values}.')
        valid_response=False
        
        if ui=="gui":
            # popup
            layout = [
                [sg.Text(prompt,key='--Prompt--')],
                [sg.InputText(key='--Input--')],
                [sg.Button('Enter', key='--Enter--', bind_return_key=True)]
            ]
            window = sg.Window('ProbeStrategy', layout, finalize=True)
            
            while True:
                event, values = window.read()
                if event=='--Enter--':
                    # validate and return
                    in_string=values['--Input--']
                    try:
                        validated_input = input_type(in_string)
                        valid_response=True
                        break
                    except ValueError:
                        # the input was invalid, so clear it and repeat loop
                        window['--Prompt--'].update(prompt + f' (must be a {input_type.__name__})')
                        window['--Input--'].update('')
                    
                    
                if event==sg.WIN_CLOSED or event=='Exit':
                    break
                    
            window.close()
            
        elif ui=="cli":
            # command line
            validated_input = click.prompt(prompt, type=input_type)
            valid_response=True
        else:
            raise ValueError("Shouldn't have got here - check ui_allowed_values!")
            
        if not valid_response:
            raise ValueError(f'ProbeStrategy.prompt_for_level(): A valid value was not obtained.')

        return validated_input