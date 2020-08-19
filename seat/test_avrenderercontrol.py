import unittest
from unittest import mock
from textwrap import dedent
import time

from avrenderercontrol import ListeningEffortPlayerAndTascarUsingOSC


class TestListeningEffortPlayerAndTascarUsingOSC(unittest.TestCase):
    # Minimal data for test cases n.b. sourceN part is arbitrary, paths are relative with UNIX style seperators
    # DATA1 = dedent("""
    #     source1/file1.wav
    #     source1/file2.wav
    #     """).strip()
    # DATA2 = dedent("""
    #     source2/file1.wav
    #     source2/file2.wav
    #     """).strip()
    # DATA3 = dedent("""
    #     source3/file1.wav
    #     source3/file2.wav
    #     """).strip()
    
    # Patch open() based on https://stackoverflow.com/a/38618056
    # Minimal data for test cases n.b. sourceN part is arbitrary, paths are relative with UNIX style seperators    
    def my_open(filename,newline=''):
        #print('Using my_open via mock.mock_open...')
        if filename == 'list1.txt':
            content = dedent("""
                source1/file1.wav
                source1/file2.wav
                """).strip()
        elif filename == 'list2.txt':
            content = dedent("""
                source2/file1.wav
                source2/file2.wav
                """).strip()
        elif filename == 'list3.txt':
            content = dedent("""
                source3/file1.wav
                source3/file2.wav
                """).strip()
        else:
            raise FileNotFoundError(filename)
        file_object = mock.mock_open(read_data=content).return_value
        #file_object.__iter__.return_value = content.splitlines(True) #think this was need in older version of python
        return file_object        
    
    # to test open locally only need to patch __main__
    @mock.patch('__main__.open', new=my_open)
    def test_patched_open(self):
        with open('list1.txt') as file:
            self.assertEqual(file.readline(),'source1/file1.wav\n')
    
    # to test with open patched in my class we need to pathc builtins (possibly we could be more restirctive)
    @mock.patch('builtins.open', new=my_open)      
    def test_full_use(self):
        """
        Test that it works
        """
        probeLevelList=[-6, -3]
        nTrials = len(probeLevelList)
        config={
            "skybox":"skyboxPath.mp4",
            "lists":['list1.txt','list2.txt','list3.txt']
        }
        
        avrenderer = ListeningEffortPlayerAndTascarUsingOSC()
        avrenderer.loadConfig(config)
        # TODO: test that empty path raises exception
        # TODO: test that non-existent path raises exception
        
        avrenderer.startScene()
        
        for probeLevel in probeLevelList:
            avrenderer.setProbeLevel(probeLevel)
            avrenderer.presentNextTrial()
            time.sleep(1)
  
  

if __name__ == '__main__':
    unittest.main()