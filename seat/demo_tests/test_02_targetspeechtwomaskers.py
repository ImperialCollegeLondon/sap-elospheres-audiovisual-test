import seat
import pathlib

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "02_TargetSpeechTwoMaskers")
    # target_video_list_file = pathlib.Path(data_root_dir, "target_video.txt")
    block_config = {
        "AVRendererControl": {
            "class": "avrenderercontrol.osc_tascar_wsl.TargetSpeechTwoMaskers",
            "settings": {
                "root_dir": data_root_dir,
                "pre_target_delay": 1.5,
                "present_target_video": True,
                "target_video_list_file": "target_video.txt"
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.fixed_probe_level.FixedProbeLevel",
            "settings": {
                "initial_probe_level": -3,
                "max_num_trials": 3
            }
        },
        "ResponseMode": {
            "class": "responsemode.speech_intelligibility.ExperimenterSelectsCorrectKeywords",
            "settings": {
                "root_dir": data_root_dir,
                "keyword_file": "keywords.txt"
            }
        }
    }
    seat.run_block(block_config)
