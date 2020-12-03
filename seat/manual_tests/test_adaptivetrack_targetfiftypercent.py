import pathlib
import responsemode
import probestrategy
from datetime import datetime

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "02_TargetSpeechTwoMaskers")
    tmp_dir = pathlib.Path(parent_directory,
                           "local_unversioned_tmp_files",
                           datetime.now().strftime("%Y%m%d_%H%M%S"))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    config = {
                "root_dir": data_root_dir,
                "keyword_file": "keywords.txt",
                "logfile": str(pathlib.Path(tmp_dir, 'response_log.csv'))
            }
    response_mode = responsemode.ExperimenterSelectsCorrectKeywords(config)

    config = {
        "initial_probe_level": -6,
        "max_num_trials": 3,
        "logfile": str(pathlib.Path(tmp_dir, 'probe_log.csv'))
    }
    probe_strategy = probestrategy.TargetFiftyPercent(config)

    while not probe_strategy.is_finished():
        probe_level = probe_strategy.get_next_probe_level()
        stimulus_id = probe_strategy.get_next_stimulus_id()
        response_mode.show_prompt(stimulus_id)
        result = response_mode.wait()
        probe_strategy.store_trial_result(result)
