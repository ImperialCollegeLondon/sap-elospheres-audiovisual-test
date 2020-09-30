import unittest
import jacktripcontrol

class TestJackTripControl(unittest.TestCase):
    def test_metronome_left(self):
        """
        Test that the metronome plays on the left channel
        """
        jtc = jacktripcontrol.JackTripControl()
        jtc.start()
        jtc.testMetronomeManual()

if __name__ == '__main__':
    unittest.main()
