from abc import ABC, abstractmethod
import numpy as np
import time
import os
import csv
from pythonosc import udp_client

class AVRendererControl(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def loadConfig(self,config):
        pass

    @abstractmethod
    def startScene(self):
        pass

    @abstractmethod        
    def setProbeLevel(self,probeLevel):
        pass
        
    @abstractmethod
    def presentNextTrial(self):
        pass
    
    
class ListeningEffortPlayerAndTascarUsingOSC(AVRendererControl):
    """
    First attempt based on python_osc_demo_v4.py
    
    Assumes a lot of things
    """    
    
    def __init__(self):
        # TODO: Check for destinations - Unity and TASCAR need to be running
        unity_ip="192.168.1.109" # windows desktop
        unity_osc_port=7000

        tascar_ip="192.168.1.118" # ubuntu desktop
        tacar_osc_port=9877

        sampler_ip="239.255.1.7" # multicast
        source1_osc_port=9001
        source2_osc_port=9003
        source3_osc_port=9005
        
        self.source1_name="source1"
        self.source2_name="source2"
        self.source3_name="source3"
        
        # open the OSC comms
        self.video_client = udp_client.SimpleUDPClient(unity_ip,unity_osc_port)
        self.tascar_client = udp_client.SimpleUDPClient(tascar_ip,tacar_osc_port)
        self.sampler_client1 = udp_client.SimpleUDPClient(sampler_ip,source1_osc_port)
        self.sampler_client2 = udp_client.SimpleUDPClient(sampler_ip,source2_osc_port)
        self.sampler_client3 = udp_client.SimpleUDPClient(sampler_ip,source3_osc_port)
        
    
    def loadConfig(self,config):
        # TODO: Actually use the configPath to get this information
        self.skybox=config["skybox"]
        source1_list=os.path.join( config["localDataRoot"], config["lists"][0])
        source2_list=os.path.join( config["localDataRoot"], config["lists"][1])
        source3_list=os.path.join( config["localDataRoot"], config["lists"][2])

        with open(source1_list, newline='') as list1, \
             open(source2_list, newline='') as list2, \
             open(source3_list, newline='') as list3:

            reader1 = csv.reader(list1, delimiter=' ')
            reader2 = csv.reader(list2, delimiter=' ')
            reader3 = csv.reader(list3, delimiter=' ')
            self.source1_path = []
            self.source2_path = []
            self.source3_path = []
            # TODO: validate that all the files are present
            # TODO: create/configure the samplers used by TASCAR here
            
            # n.b. technically don't need to enumerate here - could set maxStimulusIndex from 
            # length of the lists but previous version required the index
            for stimulusID,(row1,row2,row3) in enumerate(zip(reader1,reader2,reader3)):
                # print(stimulusID)
                # print(row1)
                # print(row2)
                # print(row3)
                self.source1_path.append(self.convertPath(row1[0]))
                self.source2_path.append(self.convertPath(row2[0]))
                self.source3_path.append(self.convertPath(row3[0]))

        
        self.maxStimulusIndex = stimulusID
        
    def startScene(self):
        # one shot for the background
        self.video_client.send_message("/video/play",[0, self.skybox] )
        self.tascar_client.send_message("/transport/locate",[0.0] )
        self.tascar_client.send_message("/transport/start",[] )
        
        self.nextStimulusIndex = 0


    def setProbeLevel(self,probeLevel):
        """
        probeLevel is scalar SNR in dB wrt background noise/interferers
        
        
        currently assuming that source 2 is the target
        """
        interfererPowerDB = -10
        self.source1_gain = np.power(10,(interfererPowerDB/20))
        self.source2_gain = np.power(10,(probeLevel/20))
        self.source3_gain = np.power(10,(interfererPowerDB/20))
        
    def presentNextTrial(self):
        """
        output the actual stimuli
        
        assumes that the config lists specify the videos to be assigned to each location
        so mapping here is 1-1
        
        """
        
        assert self.nextStimulusIndex <= self.maxStimulusIndex, "Run out of stimuli" 
        
        # start videos using '/video/play' message with payload [target screen, video path]
        self.video_client.send_message("/video/play",[1,self.source1_path[self.nextStimulusIndex]] ) 
        self.video_client.send_message("/video/play",[2,self.source2_path[self.nextStimulusIndex]] ) 
        self.video_client.send_message("/video/play",[3,self.source3_path[self.nextStimulusIndex]] ) 

        
        # TODO: calibration of offsets, or method to avoid bodge
        #time.sleep(0.180)
        
        # start audio samples using '/<source name>/<stimulus index>/add' with payload
        # [loop count, linear gain]
        
        loop_count = 1 # number of times the stimulus is played
        
        self.sampler_client1.send_message("/" + self.source1_name + "/" + 
            str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source1_gain] ) 
        self.sampler_client2.send_message("/" + self.source2_name + "/" + 
            str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source2_gain] ) 
        self.sampler_client3.send_message("/" + self.source3_name + "/" + 
            str(self.nextStimulusIndex+1) + "/add",[loop_count,self.source3_gain] ) 
        
        # increment counter
        self.nextStimulusIndex+=1
        
    # TODO: make unit test for this, once we know how data will be arranged
    def convertPath(self, ubuntuWavPath):
        windows_root="C:\\Users\\alastair\\Dropbox\\ELOSPHERES\\data\\"
        ubuntu_root="/home/amoore1/Dropbox/ELOSPHERES/data/"
        ubuntu_root="/Users/amoore1/Dropbox/ELOSPHERES/data/"
        windowsVideoPath = windows_root + '\\' + ubuntuWavPath.replace(ubuntu_root,'').replace('/','\\').replace('.wav','.mp4')
        # print(windowsVideoPath)
        return windowsVideoPath