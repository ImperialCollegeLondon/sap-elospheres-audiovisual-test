from abc import ABC, abstractmethod
import numpy as np
import time
import os
import csv
import subprocess
from pythonosc import udp_client
import confuse
import ipaddress

class AVRendererControl(ABC):
    """Abstract base class to define the interface"""

    @abstractmethod
    def loadConfig(self,config):
        pass

    def setup(self):
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
        # get the IP addresses
        appName='ListeningEffortPlayerAndTascarUsingOSC'
        self.moduleConfig = confuse.Configuration(appName, __name__)

    # implement conext manager magic
    def __enter__(self):
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        self.closeOSC()

    def setupOSC(self):
        # get the tascar ip address
        # if specified in the config use it, otherwise look in enviornment variable
        tascar_ipaddress = self.moduleConfig['tascar']['ipaddress'].get(str)
        print('config tascar.ipaddress:' + tascar_ipaddress)
        if not self.isValidIPAddress(tascar_ipaddress):
            variablename=self.moduleConfig['tascar']['ipenvvariable'].get(str)
            filename=os.environ.get(variablename)
            with open(filename, "r") as myfile:
                tascar_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(variablename, tascar_ipaddress))
            if not self.isValidIPAddress(tascar_ipaddress):
                # failed to get a valid ipaddress
                print(tascar_ipaddress)
                raise ValueError
            # store it in config in case we need it again
            self.moduleConfig['tascar']['ipaddress']=tascar_ipaddress

        # TODO: check validity of all ip addresses
        # open the OSC comms
        self.video_client = udp_client.SimpleUDPClient(
            self.moduleConfig['unity']['ipaddress'].get(str),
            self.moduleConfig['unity']['oscport'].get(int))
        self.tascar_client = udp_client.SimpleUDPClient(
            self.moduleConfig['tascar']['ipaddress'].get(str),
            self.moduleConfig['tascar']['oscport'].get(int))
        self.sampler_client1 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source1']['oscport'].get(int))
        self.sampler_client2 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source2']['oscport'].get(int))
        self.sampler_client3 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source3']['oscport'].get(int))

        # tell unity where to send the head rotation data
        self.video_client.send_message("/set_client_address",
            [self.moduleConfig['tascar']['ipaddress'].get(str),
             self.moduleConfig['tascar']['oscport'].get(int)])

    def closeOSC(self):
        # this isn't really necessary but avoids warnings in unittest
        if hasattr(self, 'video_client'):
            self.video_client._sock.close()
        if hasattr(self, 'tascar_client'):
            self.tascar_client._sock.close()
        if hasattr(self, 'sampler_client1'):
            self.sampler_client1._sock.close()
        if hasattr(self, 'sampler_client2'):
            self.sampler_client2._sock.close()
        if hasattr(self, 'sampler_client3'):
            self.sampler_client3._sock.close()

    def loadConfig(self,config):
        # TODO: Actually use the configPath to get this information
        # TODO: Check for destinations - Unity and TASCAR need to be running


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

    def getLocalIPAddress(self):
        return "127.0.0.1"

    def getWSLGuestIPAddress(self):
        result = subprocess.run(["wsl","hostname -I"], check=True)
        return result

    def getWSLHostIPAddress(self):
        result = subprocess.run(["wsl","cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f 2"], check=True)
        return result

    def isValidIPAddress(self,addressToTest):
        try:
            parsedAddress = ipaddress.ip_address(addressToTest)
            print('parsedAddress:' + str(parsedAddress))
            return True
        except ValueError as err:
            print(err)
            print('Invalid address:', addressToTest)
            return False
