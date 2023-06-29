from abc import ABC, abstractmethod
from .probe_strategy import ProbeStrategy
import numbers
import numpy as np
import pandas as pd
import pathlib
import warnings


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
            if self.display_plot:
                import matplotlib.pyplot as plt
                import seaborn as sns
        else:
            self.display_plot = False
            
        if "save_probe_history_plot" in config:
            self.save_probe_history_plot = config["save_probe_history_plot"]
            if self.save_probe_history_plot:
                if "probe_fig_save_path" in config:
                    self.probe_fig_save_path = config["probe_fig_save_path"]
                else:
                    raise ValueError("config is missing probe_fig_save_path key")
        else:
            self.save_probe_history_plot = False    
        
        if "save_regression_plot" in config:
            self.save_regression_plot = config["save_regression_plot"]
            if self.save_regression_plot:
                if "regression_fig_save_path" in config:
                    self.regression_fig_save_path = config["regression_fig_save_path"]
                else:
                    raise ValueError("config is missing regression_fig_save_path key")
        else:
            self.save_regression_plot = False
        
        self.num_response_intervals = 5  # TODO set this in config
        self.results_df = None
        self.trial_counter = 0
        self.stimulus_id = 0
        
        self.probe_level = ProbeStrategy.parse_possibly_empty_scalar_key(
            config, "initial_probe_level")
        

    def setup(self, ui="gui"):
        if self.probe_level is None:
            self.probe_level = self.prompt_for_user_input(
                prompt='Enter the initial probe level [dB] as a float:',
                ui='gui', input_type=float)

    def prepare_next_probe(self):
        num_correct = self.results_df.iloc[-1]["num_correct"]
        self.probe_level += self.step_size * self.change_vector[num_correct]
        self.trial_counter += 1
        self.stimulus_id += 1
        if self.verbosity > 3:
            print('prepare_next_probe')
            print(f'{num_correct} correct - next level {self.probe_level}')
        

    def get_current_estimate(self):
        # quick and dirty current estimate is the latest probe level
        # TODO: use the available data to form estimate
        return self.probe_level


    def is_finished(self):
        if (self.results_df is not None) and (self.results_df.shape[0] >= self.max_num_trials):
            return True
        else:
            return False

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
        
        new_row = pd.DataFrame({'trial_id': self.trial_counter,
                                'stimulus_id': self.stimulus_id,
                                'target_level': self.target_level,
                                'probe_level': self.probe_level,
                                'success_vector': [result],
                                'num_correct': np.sum(result),
                                'trial_mean': np.mean(result)})
        
        if self.results_df is None:
            self.results_df = new_row
        else:
            self.results_df = pd.concat([self.results_df, new_row],
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
                plt.savefig(self.probe_fig_save_path)
                plt.close(fig)
            if self.save_regression_plot:
                # print(self.results_df)
                
                probe_level_col = self.results_df.probe_level.values
                probe_level = np.repeat(probe_level_col, self.num_response_intervals)
                success = np.ndarray((len(self.results_df), self.num_response_intervals))
                for i,vector in enumerate(self.results_df.success_vector):
                    # print(vector)
                    success[i,:] = vector
                success = success.flatten()
                # print(success)
                # print('success shape: ' + str(np.shape(success)))
                # print(probe_level)
                # print('probe_level shape: ' + str(np.shape(probe_level)))                
                flat_df = pd.DataFrame({"probe_level": probe_level,
                                        "success": success})
                sns_plot = sns.lmplot(data=flat_df, x="probe_level", y="success",
                          logistic=True, x_estimator=np.mean)
                sns_plot.savefig(self.regression_fig_save_path)
                
    def get_next_stimulus_id(self):
        return self.stimulus_id

    def get_next_probe_level(self):
        return self.probe_level

    def get_next_probe_level_as_string(self):
        return str(self.probe_level)

    def get_trial_data(self):
        df = self.results_df.iloc[[-1],:].copy()
        # success_vector is an array which doesnt play nicely so remove it
        df.drop('success_vector', axis=1, inplace=True)
        print(df)
        print(f'df has type {type(df)} and shape {df.shape}')
        return df
    
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

        self.target_level = 0.8
        self.change_vector = [4, 3, 2, 1, 0, -1]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]


class TargetTwentyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)

        self.target_level = 0.2
        self.change_vector = [1, 0, -1, -2, -3, -4]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]


class TargetFiftyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)

        self.target_level = 0.5
        self.change_vector = [3, 2, 1, -1, -2, -3]
        self.step_size = 1.5
        self.max_num_trials = config["max_num_trials"]
        if "step_size" in config:
            self.step_size = config["step_size"]



class DualTargetTwentyEightyPercent(AdaptiveTrack):
    def __init__(self, config):
        """Constructor deals with configuring the class

        Use parent class' constuctor to create an empty DataFrame in which to
        store results
        """
        super().__init__(config)
        self.max_run_per_track = 3

        self.target_level_list = [0.2, 0.8]
        self.change_vector = [[1, 0, -1, -2, -3, -4],  # 20% target
                              [4, 3,  2,  1,  0, -1]]  # 80% target
        self.step_size = 1.5
        self.max_num_trials = int(config["max_num_trials"])
        if "step_size" in config:
            self.step_size = config["step_size"]
        if "max_run_per_track" in config:
            self.max_run_per_track = int(config["max_run_per_track"])
        
        self.num_reshuffles_before_warn = 10000   
        
        # randomly assign trials to tracks
        trials_per_track = np.zeros(2);
        trials_per_track[0] = np.round((self.max_num_trials-1)/2)
        trials_per_track[1] = self.max_num_trials - trials_per_track[0]
        rng = np.random.default_rng()
        self.track_assignment = np.concatenate(
            [np.zeros(trials_per_track[0].astype(int)),
             np.ones(trials_per_track[1].astype(int))]).astype(int)
        if self.verbosity >=3:
            print(self.track_assignment)
        shuffle_ok = False
        seg_len = self.max_run_per_track+1
        
        reshuffle_counter = 0
        while (not shuffle_ok):
            if (reshuffle_counter > self.num_reshuffles_before_warn):
                warnings.warn((f'Searching for a random sequence of length ' 
                               f'{self.max_num_trials} with a run of '
                               f'<={self.max_run_per_track} is taking a while!'
                               f'  Consider allowing longer runs or fewer trials.'))
            
            # do a new shuffle
            rng.shuffle(self.track_assignment)
            reshuffle_counter += 1
            
            # test it
            shuffle_ok=True
            for i in range(self.max_num_trials-seg_len):
                seg = self.track_assignment[i + np.arange(0,seg_len)]
                # print(f'{seg}')
                if sum(seg) in [0, seg_len]:
                    # print(f'max run exceeded {seg} sum {sum(seg)}')
                    shuffle_ok = False
         

        self.target_level = self.target_level_list[self.trial_counter]
        
        
    def prepare_next_probe(self):
        # get entries from dataframe which correspond to the current target
        next_trial = self.trial_counter + 1
        target_level_index = self.track_assignment[next_trial]
        track_df = self.results_df[self.results_df.target_level==self.target_level_list[target_level_index]]
        if len(track_df)==0:
            # select the first element
            num_correct = self.results_df.iloc[0]["num_correct"]
            prev_probe_level = self.results_df.iloc[0]["probe_level"]
        else:
            # select the most recent element of this track
            num_correct = track_df.iloc[-1]["num_correct"]
            prev_probe_level = track_df.iloc[-1]["probe_level"]
            
        if self.verbosity >=3:
            print('num_correct: ' + num_correct)
        self.probe_level = prev_probe_level + \
            self.step_size * self.change_vector[target_level_index][num_correct]
        self.trial_counter += 1
        self.stimulus_id += 1
        self.target_level = self.target_level_list[
            self.track_assignment[self.trial_counter]]

    def get_current_estimate(self):
        # TODO: use all available data to form estimate
        return np.mean(self.results_df.probe_level[-self.num_trials_to_average:])
