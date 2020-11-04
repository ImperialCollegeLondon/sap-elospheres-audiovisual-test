import unittest
from . import _root,TempDir #shorthand to create confuse config structure
import confuse
from textwrap import dedent
from avrenderercontrol import TargetToneInNoise



class TestTargetToneInNoise(unittest.TestCase):
    def test_load_config_path_resolution(self):
        """
        Test that paths are resolved correctly
        """
        #correct values - note indirection due to listening_condition_id in blocks
        skybox_absolute_path_block0 = 'C:\\path\\to\\root\\skybox_dir\\filename1.mp4'
        skybox_absolute_path_block1 = 'C:\\path\\to\\root\\skybox_dir\\filename0.mp4'


        my_dict={
            'state_control':{'current_block_index': 0},
            'paths': {
              'unity_data':{
                'root_dir': 'C:/path/to/root',
                'skybox_rel_dir': 'skybox_dir'
                }
            },
            'listening_conditions':[{
                'id': '0',
                'avrenderer':{
                    'class': 'ListeningEffortPlayerAndTascarUsingOSC',
                    'tascar_scn_file': '00_binaural_demo.tsc',
                    'skybox_file': 'filename0.mp4'
                    }
                },{
                'id': '1',
                'avrenderer':{
                    'class': 'ListeningEffortPlayerAndTascarUsingOSC',
                    'tascar_scn_file': '01_three_anechoic_sources_native_binaural.tsc',
                    'skybox_file': 'filename1.mp4'
                    }
                }
            ],
            'blocks': [{
                'id': '1',
                'listening_condition_id': '1',
                'stimuli_list': ''
                },{
                'id': 'bob',
                'listening_condition_id': '0',
                'stimuli_list': ''
                }
            ]
        }

        config = _root(my_dict)
        avrenderer = TargetToneInNoise()


        # test paths
        avrenderer.load_config(config)
        self.assertEqual(str(avrenderer.skybox_absolute_path),skybox_absolute_path_block0)

        # Second test - modify the block to use
        config["state_control"]["current_block_index"]=1
        avrenderer.load_config(config)
        self.assertEqual(str(avrenderer.skybox_absolute_path),skybox_absolute_path_block1)

if __name__ == '__main__':
    unittest.main()
