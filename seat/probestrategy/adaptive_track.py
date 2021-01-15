from abc import ABC, abstractmethod
from .probe_strategy import ProbeStrategy
import numpy as np
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import seaborn as sns


class AdaptiveTrack(ProbeStrategy, ABC):
    """
    Probe level is varied in an attempt to converge on a certain response
    success rate.
    Stimuli are presented in sequence.
    Stopping criterion is the lower of a convergence criterion or the
    predetermined maximum number of trials.
    """
    def __init__(self, config):
        """Deal with common intialsisation in this parent class"""
        self.write_to_log = False
        if "log_path" in config:
            print(config["log_path"])
            self.write_to_log = True
            self.log_path = pathlib.Path(config["log_path"])
            self.log_path.touch(exist_ok=False)  # do NOT overwrite!

        
        if "verbosity" in config:
            self.verbosity = config["verbosity"]
        else:
            self.verbosity = 0
            
        if "num_trials_to_average" in config:
            self.num_trials_to_average = config["num_trials_to_average"]
        else:
            self.num_trials_to_average = 1
        
        
        if "display_plot" in config:
            self.display_plot = config["display_plot"]
        else:
            self.display_plot = False
            
        if "save_probe_history_plot" in config:
            self.save_probe_history_plot = config["save_probe_history_plot"]
            if self.save_probe_history_plot:
                if "fig_save_path" in config:
                    self.fig_save_path = config["fig_save_path"]
                else:
                    raise ValueError("config is missing fig_save_path key")
        else:
            self.save_probe_history_plot = False    
        self.save_probe_history_plot
        self.num_response_intervals = 5  # TODO set this in config
        self.results_df = pd.DataFrame(
            columns=['trial_id',
                     'stimulus_id',
                     'target_level',
                     'probe_level',
                     'success_vector',
                     'trial_mean'], dtype=float)
        self.trial_counter = 0
        self.stimulus_id = 0

    @abstractmethod
    def prepare_next_probe(self):
        """This is private and must be overriden by child class"""
        pass

    def validate_result(self, result):
        """Raise exception if result does not match the expected form"""
        if len(result) is not self.num_response_intervals:
            raise ValueError("result should contain %d entries" %
                             self.num_response_intervals)
        for element in result:
            if element not in (True, False):
                raise ValueError("all elements of result must be booleans")

    def store_trial_result(self, result):
        result = np.array(result)
        self.validate_result(result)
        if self.verbosity > 2:
            print('result: ' + str(result))
            print('trial_counter: ' + str(self.trial_counter))
        self.results_df = self.results_df.append({
            'trial_id': self.trial_counter,
            'stimulus_id': self.stimulus_id,
            'target_level': self.target_level,
            'probe_level': self.probe_level,
            'success_vector': result,
            'trial_mean': np.mean(result)},
            ignore_index=True)
        if self.verbosity > 2:
            print(self.results_df)
        if self.verbosity > 3:
            print(len(self.results_df))

        if self.write_to_log:
            df_to_write = self.results_df.iloc[self.trial_counter:self.trial_counter+1]
            # n.b. simply picking a single element (as below) doesnt work...
            # the entries end up as a column
            # df_to_write = self.results_df.iloc[self.trial_counter]
            # print(self.trial_counter)
            write_header = (self.trial_counter == 0)
            # print(df_to_write.to_csv(index=False,
            #                    header=write_header,
            #                    mode='a'))
            df_to_write.to_csv(self.log_path,
                               index=False, header=write_header,
                               mode='a')

        # plot the result
        if self.display_plot:
            if self.verbosity >= 3:
                print('plotting probe_level over time')
            # create fig on first iteration    
            if len(self.results_df.trial_id)==1:
                self.fig, self.ax = plt.subplots()
            self.ax.cla()
            sns.lineplot(data=self.results_df, x="trial_id", y="probe_level",
                      ax=self.ax, hue="target_level")
            # if len(self.results_df.trial_id)==1:
                # self.line, = self.ax.plot(self.results_df.target_level)
                # self.ax.set_xlim([0, self.max_num_trials])
            self.ax.set_xlim([0, self.max_num_trials])
            if len(self.results_df.trial_id)==1:
                plt.ion()
                plt.show()
            else:
                # print('trial_id type: ' + str(type(self.results_df.trial_id)))
                # print('target_level type: ' + str(type(self.results_df.target_level)))
                # self.line.set_xdata(self.results_df.trial_id)
                # self.line.set_xdata(self.results_df.target_level)
                plt.pause(0.1)
            
        
        if not self.is_finished():
            # work out where to go next, implemented by child class
            self.prepare_next_probe()
        else:
            if self.save_probe_history_plot:
                fig, ax = plt.subplots()
                sns.lineplot(data=self.results_df, x="trial_id", y="probe_level",
                          ax=ax, hue="target_level")
                plt.savefig(self.fig_save_path)

    def get_next_stimulus_id(self):
        return self.stimulus_id

    def get_next_probe_level(self):
        return self.probe_level

    def get_next_probe_level_as_string(self):
        return str(self.probe_level)

    # def display_pyschometric_curve(self):
    #     probed_levels = self.results_df.probe_level.unique()
    #     for ilevel, probe_level in enumerate(probed_levels):
    #         matched_df = self.results_df.success_vector[self.results_df.probe_level == probe_level]
    #         print(matched_df.shape)
    #         print(matched_df)
    #         print('mean: ' + str(np.mean(matched_df.stack())))
    #         # mean[ilevel] = np.mean(matched_df)
    #         # num_elements[ilevel] = np.mean()

# TODO: Figure out how extract the required datra


class TargetEightyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)

        self.probe_level = config["initial_probe_level"]
        self.target_level = 0.8
        self.change_vector = [4, 3, 2, 1, 0, -1]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]

    def prepare_next_probe(self):
        success_vector = self.results_df.iloc[-1]["success_vector"]
        num_correct = np.sum(success_vector)
        self.probe_level += self.step_size * self.change_vector[num_correct]
        self.trial_counter += 1
        self.stimulus_id += 1

    def get_current_estimate(self):
        # quick and dirty current estimate is the latest probe level
        # TODO: use the available data to form estimate
        return self.probe_level

    def is_finished(self):
        if (len(self.results_df) >= self.max_num_trials):
            return True
        else:
            return False


class TargetTwentyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)

        self.probe_level = config["initial_probe_level"]
        self.target_level = 0.2
        self.change_vector = [1, 0, -1, -2, -3, -4]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]

    def prepare_next_probe(self):
        success_vector = self.results_df.iloc[-1]["success_vector"]
        num_correct = np.sum(success_vector)
        self.probe_level += self.step_size * self.change_vector[num_correct]
        self.trial_counter += 1
        self.stimulus_id += 1

    def get_current_estimate(self):
        # quick and dirty current estimate is the latest probe level
        # TODO: use the available data to form estimate
        return self.probe_level

    def is_finished(self):
        if (len(self.results_df) >= self.max_num_trials):
            return True
        else:
            return False


class TargetFiftyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)

        self.probe_level = config["initial_probe_level"]
        self.target_level = 0.5
        self.change_vector = [3, 2, 1, -1, -2, -3]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]
        if "step_size" in config:
            self.step_size = config["step_size"]

    def prepare_next_probe(self):
        success_vector = self.results_df.iloc[-1]["success_vector"]
        num_correct = np.sum(success_vector)
        self.probe_level += self.step_size * self.change_vector[num_correct]
        self.trial_counter += 1
        self.stimulus_id += 1

    def get_current_estimate(self):
        # TODO: use all available data to form estimate
        return np.mean(self.results_df.probe_level[-self.num_trials_to_average:])

    def is_finished(self):
        if (len(self.results_df) >= self.max_num_trials):
            return True
        else:
            return False
