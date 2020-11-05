import unittest
from . import _root  # shorthand to create confuse config structure
from avrenderercontrol import TargetToneInNoise

class TestTargetToneInNoise(unittest.TestCase):
    def test_load_config_path_resolution(self):
        """
        Test that paths are resolved correctly
        """
        # TODO add unit tests
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
