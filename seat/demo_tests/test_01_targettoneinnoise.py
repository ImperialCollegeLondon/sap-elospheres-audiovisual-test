import seat
import pathlib

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    data_root_dir = pathlib.Path("demo_data", "01_TargetToneInNoise")
    block_config = {
        "AVRendererControl": {
            "class": "avrenderercontrol.osc_tascar_wsl.TargetToneInNoise",
            "settings": {
                "root_dir": data_root_dir
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.fixed_probe_level.FixedProbeLevel",
            "settings": {
                "initial_probe_level": -3,
                "max_num_trials": 2
            }
        }
    }
    seat.run_block(block_config)
