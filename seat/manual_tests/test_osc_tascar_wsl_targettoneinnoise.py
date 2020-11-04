import avrenderercontrol
import confuse
import time

# Settings
# - blocks and statecontrol.current_block_index used to get listening_condition
config_source_dict = {
    'state_control': {'current_block_index': 0},
    'paths': {
      'unity_data': {
        'root_dir': 'C:/path/to/root',
        'skybox_rel_dir': 'skybox_dir'
        }
    },
    'listening_conditions': [{
        'id': '0',
        'avrenderer': {
            'class': 'avrenderercontrol.osc_tascar_wsl.TargetToneInNoise',
            'tascar_scn_file': '00_binaural_demo.tsc',
            'skybox_file': 'filename0.mp4'
            }
        }
    ],
    'blocks': [{
        'id': '1',
        'listening_condition_id': '0',
        'stimuli_list': ''
        }
    ]
}
config = _root(my_dict)
probe_level = 0.6

# Setup
module_name, class_name = config."module.submodule.MyClass".rsplit(".", 1)
MyClass = getattr(importlib.import_module(module_name), class_name)
instance = MyClass()

avrenderer = TargetToneInNoise()
avrenderer.load_config(config)
avrenderer.setup()

# Dummy test
avrenderer.start_scene()
time.sleep(4)
for trial_num in range(5):
    avrenderer.set_probe_level(probe_level)
    avrenderer.presentNextTrial()
    time.sleep(3)
