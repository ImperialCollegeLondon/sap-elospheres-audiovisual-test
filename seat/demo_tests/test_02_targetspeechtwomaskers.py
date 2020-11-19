import seat
import pathlib

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    data_root_dir = pathlib.Path("demo_data", "02_TargetSpeechTwoMaskers")
    block_config = {
        "AVRendererControl": {
            "class": "avrenderercontrol.osc_tascar_wsl.TargetSpeechTwoMaskers",
            "settings": {
                "root_dir": data_root_dir,
                "pre_target_delay": 1.5,
                "present_target_video": False
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.fixed_probe_level.FixedProbeLevel",
            "settings": {
                "initial_probe_level": -3,
                "max_num_trials": 3
            }
        }
    }
    seat.run_block(block_config)
