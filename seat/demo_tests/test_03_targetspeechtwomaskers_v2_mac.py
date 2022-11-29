import seat
import pathlib
import util
from datetime import datetime

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "03_TargetSpeechTwoMaskers_v2")
    tmp_dir = pathlib.Path(parent_directory,
                           "local_unversioned_tmp_files",
                           datetime.now().strftime("%Y%m%d_%H%M%S"))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    block_config = {
        "App": {
            "log_dir": tmp_dir
        },
        "AVRendererControl": {
            "class": "avrenderercontrol.lep_tascar_osc.TargetSpeechTwoMaskers",
            "settings": {
                "TascarCommandLineInterface": {
                    "class": 'avrenderercontrol.tascar_cli.TascarCliMacLocal',
                    "settings": {
                        "scene_path": str(pathlib.Path(data_root_dir, 'tascar_scene_native.tsc'))
                    },
                },
                "datalogging_dir": str(tmp_dir),
                "skybox_path":
                    str(pathlib.Path(data_root_dir, 'skybox.mp4')),
                "named_locations": {
                    "left": {
                        "tascar": {
                            "x": -1.1634517053048947,
                            "y": 1.6185061721918559,
                            "z":  0.1636
                        },
                        "unity": {
                            "rot_X_deg": 4.692,
                            "rot_Y_deg": -125.71,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "middle": {
                        "tascar": {
                            "x": 0.1491,
                            "y": 1.9877,
                            "z": 0.1636
                        },
                        "unity": {
                            "rot_X_deg": 4.692,
                            "rot_Y_deg": -85.71,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "right": {
                        "tascar": {
                            "x": 1.39,
                            "y": 1.4268,
                            "z": 0.1636
                        },
                        "unity": {
                            "rot_X_deg": 4.692,
                            "rot_Y_deg": -45.71,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    }
                },
                "cue_duration": 2.0,
                "target_names": ['target'],
                "masker_names": ['masker1', 'masker2'],
                "sources": {
                    "target": {
                        "present_video": False,
                        "video_paths_file": str(pathlib.Path(data_root_dir, 'target_video.txt')),
                        "present_cue_video": False,
                        "cue_videos_paths_file": str(pathlib.Path(data_root_dir, 'target_cue_video.txt')),
                        "locations_file": str(pathlib.Path(data_root_dir, 'target_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source2',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9003,
                        "video_id": 2
                    },
                    "masker1": {
                        "present_video": False,
                        "video_paths_file": str(pathlib.Path(data_root_dir, 'masker1_video.txt')),
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'masker1_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source1',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9001,
                        "video_id": 1
                        
                    },
                    "masker2": {
                        "present_video": False,
                        "video_paths_file": str(pathlib.Path(data_root_dir, 'masker2_video.txt')),
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'masker2_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source3',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9005,
                        "video_id": 3
                        
                    }
                }
            }
        },
        "ProbeStrategy": {
            "class": "probestrategy.adaptive_track.TargetFiftyPercent",
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
