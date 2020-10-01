import unittest

from probestrategy import FixedProbeLevel


class TestFixedProbeLevel(unittest.TestCase):
    def test_end_criterion(self):
        """
        Test that it loops the correct number if times
        """
        probeLevel=0.6
        dummyData = [1,2,3,4,5,6,7,8,9,10]
        nTrials = len(dummyData)
        ps = FixedProbeLevel(0.6,nTrials)
        for data in dummyData:
            # in the loop shouldn't be finished yet
            self.assertFalse(ps.isFinished())

            # feed in data
            ps.storeTrialResult(data)

        #
        self.assertTrue(ps.isFinished())

    def test_mean(self):
        """
        Test that the current estimate is correct
        """
        probeLevel=0.6
        dummyData = [10,10,40,10]
        cumMean = [10,10,20,70/4]
        nTrials = len(dummyData)
        ps = FixedProbeLevel(0.6,nTrials)
        for data,avg in zip(dummyData,cumMean):

            # feed in data
            ps.storeTrialResult(data)

            # check estimated
            self.assertEqual(ps.getCurrentEstimate(),avg)


if __name__ == '__main__':
    unittest.main()
