import seat
import pathlib
from datetime import datetime

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "04_3av_2ao")
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
                    "class": 'avrenderercontrol.tascar_cli.MacLocal',
                    "settings": {
                        "scene_path": str(pathlib.Path(data_root_dir, 'tascar_scene_native.tsc'))
                    },
                },
                "skybox_path":
                    str(pathlib.Path(data_root_dir, 'skybox.mp4')),
                "named_locations": {
                    "left": {
                        "tascar": {
                            "x": 1.7321,
                            "y": 1.0,
                            "z": 0.0
                        },
                        "unity": {
                            "rot_X_deg": 0.0,
                            "rot_Y_deg": 0.0,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "front": {
                        "tascar": {
                            "x": 2.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "unity": {
                            "rot_X_deg": 0.0,
                            "rot_Y_deg": 0.0,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "right": {
                        "tascar": {
                            "x": 1.7321,
                            "y": -1.0,
                            "z": 0.0
                        },
                        "unity": {
                            "rot_X_deg": 0.0,
                            "rot_Y_deg": 0.0,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "far_left": {
                        "tascar": {
                            "x": 0.0,
                            "y": 2.0,
                            "z": 0.0
                        },
                        "unity": {
                            "rot_X_deg": 0.0,
                            "rot_Y_deg": 0.0,
                            "rot_Z_deg": 0.0,
                            "quad_x_euler": 0.0,
                            "quad_y_euler": 0.0,
                            "quad_x_scale": 167.0,
                            "quad_y_scale": 97.0
                        }
                    },
                    "far_right": {
                        "tascar": {
                            "x": 0.0,
                            "y": -2.0,
                            "z": 0.0
                        },
                        "unity": {
                            "rot_X_deg": 0.0,
                            "rot_Y_deg": 0.0,
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
                "masker_names": ['av_masker1', 'av_masker2','ao_masker1','ao_masker2'],
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
                    "av_masker1": {
                        "present_video": False,
                        "video_paths_file": str(pathlib.Path(data_root_dir, 'av_masker1_video.txt')),
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'av_masker1_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source1',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9001,
                        "video_id": 1

                    },
                    "av_masker2": {
                        "present_video": False,
                        "video_paths_file": str(pathlib.Path(data_root_dir, 'av_masker2_video.txt')),
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'av_masker2_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source3',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9005,
                        "video_id": 3

                    },
                    "ao_masker1": {
                        "present_video": False,
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'ao_masker1_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source4',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9007,
                        "video_id": []

                    },
                    "ao_masker2": {
                        "present_video": False,
                        "present_cue_video": False,
                        "locations_file": str(pathlib.Path(data_root_dir, 'ao_masker2_location.txt')),
                        "tascar_scene": 'point_sources',
                        "tascar_source": 'source5',
                        "sampler_ip_address": '239.255.1.7',
                        "sampler_osc_port": 9009,
                        "video_id": []

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
