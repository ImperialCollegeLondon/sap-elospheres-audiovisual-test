import seat
import pathlib
from datetime import datetime

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "01_TargetToneInNoise")
    tmp_dir = pathlib.Path(parent_directory,
                           "local_unversioned_tmp_files",
                           datetime.now().strftime("%Y%m%d_%H%M%S"))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    block_config = {
        "App": {
            "log_dir": tmp_dir
        },
        "AVRendererControl": {
            "class": "avrenderercontrol.osc_tascar_wsl.TargetToneInNoise",
            "settings": {
                "tascar_scene_path":
                    str(pathlib.Path(data_root_dir, 'tascar_scene.tsc')),
                "skybox_path":
                    str(pathlib.Path(data_root_dir, 'skybox.mp4'))
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.fixed_probe_level.FixedProbeLevel",
            "settings": {
                "initial_probe_level": -3,
                "max_num_trials": 2
            }
        },
        "ResponseMode": {
            "class": "responsemode.signal_detection.BinaryChoice",
            "settings": {
                # This is a bit of a hack!
                "signal_present": [True, True]
            }
        }
    }
    seat.run_block(block_config)
