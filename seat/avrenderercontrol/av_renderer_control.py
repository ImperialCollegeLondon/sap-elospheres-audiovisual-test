from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import time
import os
import csv
import subprocess
from pythonosc import udp_client
import confuse
import ipaddress
import pathlib


class AVRCState(Enum):
    """Enumerate states"""
    INIT = 0
    CONFIGURED = 1
    READY_TO_START = 2
    ACTIVE = 3
    TERMINATED = 4


class AVRendererControl(ABC):
    """Abstract base class to define the interface"""
    def __init__(self):
        self.probe_level = None
        self.state = AVRCState.INIT

    def is_configured(self):
        return self.is_configured

    @abstractmethod
    def load_config(self, config):
        """
        Call `load_config(config)` to pass the required settings, overriding
        any defaults which have been set

        Note: calling load_config() may be optional, depending on the
        implementation
        """
        pass

    def setup(self):
        """
        Call `setup()` after `load_config()` to get everything prepared
        """
        pass

    @abstractmethod
    def start_scene(self):
        """
        The audio visual scene will start including any continuous background
        material (noise/maskers) and/or any idle material which is active only
        between trials
        """
        pass

    @abstractmethod
    def set_probe_level(self, probe_level):
        """
        Adjust the independent parameter which is being controlled

        Depending on the implementation probe_level could be anything so
        subclasses must implement and do all validation themselves
        """
        pass

    @abstractmethod
    def present_trial(self, stimulus_id):
        """Trigger trial using stimulus given by stimulus_id (0-based)"""
        pass




    #
    #
    # def loadConfig(self,config):
    #     # TODO: Actually use the configPath to get this information
    #     # TODO: Check for destinations - Unity and TASCAR need to be running
    #
    #
    #     self.skybox=config["skybox"]
    #     source1_list=os.path.join( config["localDataRoot"], config["lists"][0])
    #     source2_list=os.path.join( config["localDataRoot"], config["lists"][1])
    #     source3_list=os.path.join( config["localDataRoot"], config["lists"][2])
    #
    #     with open(source1_list, newline='') as list1, \
    #          open(source2_list, newline='') as list2, \
    #          open(source3_list, newline='') as list3:
    #
    #         reader1 = csv.reader(list1, delimiter=' ')
    #         reader2 = csv.reader(list2, delimiter=' ')
    #         reader3 = csv.reader(list3, delimiter=' ')
    #         self.source1_path = []
    #         self.source2_path = []
    #         self.source3_path = []
    #         # TODO: validate that all the files are present
    #         # TODO: create/configure the samplers used by TASCAR here
    #
    #         # n.b. technically don't need to enumerate here - could set maxStimulusIndex from
    #         # length of the lists but previous version required the index
    #         for stimulusID,(row1,row2,row3) in enumerate(zip(reader1,reader2,reader3)):
    #             # print(stimulusID)
    #             # print(row1)
    #             # print(row2)
    #             # print(row3)
    #             self.source1_path.append(self.convertPath(row1[0]))
    #             self.source2_path.append(self.convertPath(row2[0]))
    #             self.source3_path.append(self.convertPath(row3[0]))
    #
    #
    #     self.maxStimulusIndex = stimulusID
    #
    #
    #
    #
    # def startScene(self):
    #     # one shot for the background
    #     self.video_client.send_message("/video/play",[0, self.skybox] )
    #     self.tascar_client.send_message("/transport/locate",[0.0] )
    #     self.tascar_client.send_message("/transport/start",[] )
    #
    #     self.nextStimulusIndex = 0
    #
    #
    # def setProbeLevel(self,probeLevel):
    #     """
    #     probeLevel is scalar SNR in dB wrt background noise/interferers
    #
    #
    #     currently assuming that source 2 is the target
    #     """
    #     interfererPowerDB = -10
    #     self.source1_gain = np.power(10,(interfererPowerDB/20))
    #     self.source2_gain = np.power(10,(probeLevel/20))
    #     self.source3_gain = np.power(10,(interfererPowerDB/20))
    #
    # def presentNextTrial(self):
    #     """
    #     output the actual stimuli
    #
    #     assumes that the config lists specify the videos to be assigned to each location
    #     so mapping here is 1-1
    #
    #     """
    #
    #     assert self.nextStimulusIndex <= self.maxStimulusIndex, "Run out of stimuli"
    #
    #     # start videos using '/video/play' message with payload [target screen, video path]
    #     self.video_client.send_message("/video/play",[1,self.source1_path[self.nextStimulusIndex]] )
    #     self.video_client.send_message("/video/play",[2,self.source2_path[self.nextStimulusIndex]] )
    #     self.video_client.send_message("/video/play",[3,self.source3_path[self.nextStimulusIndex]] )
    #
    #
    #     # TODO: calibration of offsets, or method to avoid bodge
    #     #time.sleep(0.180)
    #
    #     # start audio samples using '/<source name>/<stimulus index>/add' with payload
    #     # [loop count, linear gain]
    #
    #     loop_count = 1 # number of times the stimulus is played
    #
    #     self.sampler_client1.send_message("/" + self.source1_name + "/" +
    #         str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source1_gain] )
    #     self.sampler_client2.send_message("/" + self.source2_name + "/" +
    #         str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source2_gain] )
    #     self.sampler_client3.send_message("/" + self.source3_name + "/" +
    #         str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source3_gain] )
    #
    #     # increment counter
    #     self.nextStimulusIndex+=1
    #
    # # TODO: make unit test for this, once we know how data will be arranged
    # def convertPath(self, ubuntuWavPath):
    #     windows_root="C:\\Users\\alastair\\Dropbox\\ELOSPHERES\\data\\"
    #     ubuntu_root="/home/amoore1/Dropbox/ELOSPHERES/data/"
    #     ubuntu_root="/Users/amoore1/Dropbox/ELOSPHERES/data/"
    #     windowsVideoPath = windows_root + '\\' + ubuntuWavPath.replace(ubuntu_root,'').replace('/','\\').replace('.wav','.mp4')
    #     # print(windowsVideoPath)
    #     return windowsVideoPath
    #
    # def getLocalIPAddress(self):
    #     return "127.0.0.1"
    #
    # def getWSLGuestIPAddress(self):
    #     result = subprocess.run(["wsl","hostname -I"], check=True)
    #     return result
    #
    # def getWSLHostIPAddress(self):
    #     result = subprocess.run(["wsl","cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f 2"], check=True)
    #     return result
