import seat
import pathlib
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

    block_config = {
        "App": {
            "log_dir": tmp_dir
        },
        "AVRendererControl": {
            "class": "avrenderercontrol.osc_tascar_wsl.TargetSpeechTwoMaskers",
            "settings": {
                "pre_target_delay": 1.5,
                "present_target_video": True,
                "tascar_scene_path":
                    str(pathlib.Path(data_root_dir, 'tascar_scene.tsc')),
                "skybox_path":
                    str(pathlib.Path(data_root_dir, 'skybox.mp4')),
                "target_video_list_path":
                    str(pathlib.Path(data_root_dir, 'target_video.txt'))
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.adaptive_track.TargetTwentyPercent",
            "settings": {
                "initial_probe_level": -6,
                "max_num_trials": 3,
            }
        },
        "ResponseMode": {
            "class":
                "responsemode.speech_intelligibility.ExperimenterSelectsCorrectKeywords",
            "settings": {
                "keywords_path":
                    str(pathlib.Path(data_root_dir, 'keywords.txt')),
            }
        }
    }
    seat.run_block(block_config)
