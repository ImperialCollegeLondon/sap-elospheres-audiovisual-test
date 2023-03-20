from .probe_strategy import ProbeStrategy
import numbers
import numpy as np
import pandas as pd


class FixedProbeLevel(ProbeStrategy):
    """
    The probe level does not change.
    Stimuli are presented in sequence.
    Stopping criterion is the predetermined number of trials.
    """
    def __init__(self, config):
        self.fixed_level = ProbeStrategy.parse_possibly_empty_scalar_key(
            config, "initial_probe_level")
        self.num_trials = config["max_num_trials"]
        self.results_df = None
        self.next_stimulus_id = 0

    def setup(self, ui="gui"):
        print(f'In fixed_probe_level.FixedProbeLevel: self.fixed_level: {self.fixed_level}')
        if self.fixed_level is None:
            self.fixed_level = self.prompt_for_user_input(
                prompt='Enter the probe level [dB] as a float:',
                ui='gui', input_type=float)

    def store_trial_result(self, result):
        """
        result should be boolean or 0/1
        """
        # print(result)
        # print(type(result))
        
        # explicit conversion to array - will fail in invalid input
        result = np.array(result).reshape(1,-1)
        
        if not np.array_equal(result, result.astype(bool)):
            raise ValueError(f'rusult should be array-like of booleans')
        
        result = result.astype(bool)
              
        new_row = pd.DataFrame({'probe_level': self.get_next_probe_level(),
                                'result_vector': [result],
                                'num_correct': np.sum(result),
                                'trial_mean': np.mean(result)})
        
                                
        if self.results_df is None:
            self.results_df = new_row
        else:
            self.results_df = pd.concat([self.results_df, new_row], ignore_index=True)                     
        # print(self.results_df)
        
        # Storing result indicate trial finished, so increment counter
        self.next_stimulus_id += 1

    def get_next_stimulus_id(self):
        return self.next_stimulus_id

    def get_next_probe_level(self):
        return self.fixed_level

    def get_next_probe_level_as_string(self): 
        return str(self.get_next_probe_level())

    def get_current_estimate(self):
        if self.results_df is None:
            return None
        else:
            return np.mean(self.results_df['trial_mean'])

    def is_finished(self):
        if (self.results_df is not None) and (self.results_df.shape[0] >= self.num_trials):
            return True
        else:
            return False

    def get_trial_data(self):
        """
        Get the result of the most recent trial
        Returns
        -------
        DataFrame.
            single row with columns 'probe_level' and 'result'
        """
        return self.results_df.tail(1)

        
class MultipleFixedProbeLevels(FixedProbeLevel):
    """
    The probe level changes using a predetermined sequence.
    Stimuli are presented in sequence.
    Stopping criterion is the predetermined number of trials.
    """
    def __init__(self, config):
        super().__init__(config)
        
        # probe level variations stored as one per line
        # we could make this much more elaborate but this is ok for now
        with open(config["probe_level_variations_file"]) as f:
                self.probe_level_offsets = [float(line.strip()) for line in f]
        
        if len(self.probe_level_offsets) < self.num_trials:
            raise ValueError(f'MultipleFixedProbeLevels: number of offsets is less than the number of trials')
            
    def get_next_probe_level(self):
        # print(f'next_stimulus_id: {self.next_stimulus_id}')
        # print(f'fixed_level: {self.fixed_level}')
        # print(f'probe_level_offsets: {self.probe_level_offsets}')
        return self.fixed_level + self.probe_level_offsets[self.next_stimulus_id]
        