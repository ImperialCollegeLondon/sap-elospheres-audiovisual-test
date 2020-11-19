# from .av_renderer_control import AVRendererControl
import avrenderercontrol.av_renderer_control as avrc
import confuse
import pathlib
import pandas as pd
import numpy as np
import pprint
import ipaddress
import os
import errno
from pythonosc import udp_client
import time
import subprocess

# helper functions
# leading underscore avoids being imported


def _is_valid_ipaddress(address_to_test):
    """Private function to check validity of an ip address"""
    try:
        parsed_address = ipaddress.ip_address(address_to_test)
        print('parsed address:' + str(parsed_address))
        return True
    except ValueError as err:
        print(err)
        print('Invalid address:', address_to_test)
        return False


def check_path_is_file(pathlib_path):
    if not pathlib_path.is_file():
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(pathlib_path))


def convert_windows_path_to_wsl(pathlib_win_path):
    wsl_command = ("wsl bash -c \"wslpath '"
                   + str(pathlib_win_path)
                   + "'\"")
    try:
        result = subprocess.run(wsl_command,
                                capture_output=True,
                                check=True,
                                text=True)
        return result.stdout.rstrip()

    except subprocess.CalledProcessError as error:
        print('Path conversion using wslpath failed')
        print(wsl_command)
        raise error


class ListeningEffortPlayerAndTascarUsingOSCBase(avrc.AVRendererControl):
    """
    Base class to implement core functionality of co-ordinating the unity-based
    visual display with headtracking data sent via osc to tascar-based audio
    renderer running on windows subsytem for linux
    """
    def __init__(self):
        # get the IP addresses
        app_name = 'ListeningEffortPlayerAndTascarUsingOSC'
        self.moduleConfig = confuse.Configuration(app_name, __name__)

    # implement conext manager magic
    def __enter__(self):
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_scene()
        self.close_osc()

    def setup_osc(self):
        # get the tascar ip address
        # if specified in the config use it, otherwise look in enviornment
        # variable
        tascar_ipaddress = self.moduleConfig['tascar']['ipaddress'].get(str)
        print('config tascar.ipaddress:' + tascar_ipaddress)
        if not _is_valid_ipaddress(tascar_ipaddress):
            env_variable_name = self.moduleConfig['tascar']['ipenvvariable'] \
                .get(str)
            filename = os.environ.get(env_variable_name)
            print('Reading tascar IP address from ' + filename)
            with open(filename, "r") as myfile:
                tascar_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(env_variable_name, tascar_ipaddress))
            if not _is_valid_ipaddress(tascar_ipaddress):
                # failed to get a valid ipaddress
                print(tascar_ipaddress)
                raise ValueError
            # store it in config in case we need it again
            self.moduleConfig['tascar']['ipaddress'] = tascar_ipaddress

        sampler_ipaddress = self.moduleConfig['sampler']['ipaddress'].get(str)
        print('config tascar.ipaddress:' + sampler_ipaddress)
        if not _is_valid_ipaddress(sampler_ipaddress):
            env_variable_name = self.moduleConfig['tascar']['ipenvvariable'] \
                .get(str)
            filename = os.environ.get(env_variable_name)
            print('Reading tascar IP address from ' + filename)
            with open(filename, "r") as myfile:
                sampler_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(env_variable_name, sampler_ipaddress))
            if not _is_valid_ipaddress(sampler_ipaddress):
                # failed to get a valid ipaddress
                print(sampler_ipaddress)
                raise ValueError
            # store it in config in case we need it again
            self.moduleConfig['sampler']['ipaddress'] = sampler_ipaddress

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
        self.video_client.send_message("/set_client_address", [
            self.moduleConfig['tascar']['ipaddress'].get(str),
            self.moduleConfig['tascar']['oscport'].get(int)
            ])

    def close_osc(self):
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

    def start_scene(self):
        """
        Basic implementation - subclasses may need to override
        """
        if self.state == avrc.AVRCState.READY_TO_START:

            wsl_command = 'wsl ' \
                + '-u root bash -c \"/usr/bin/tascar_cli ' \
                + str(self.tascar_scn_file_wsl_path) \
                + '\"'
            # print(wsl_command)
            self.tascar_process = subprocess.Popen(
                wsl_command, creationflags=subprocess.CREATE_NEW_CONSOLE)

            # give tascar a chance to start
            time.sleep(1)

            if self.tascar_process.poll() is not None:
                print('Process didn''t start right')
                print(self.tascar_process)

            # check that the process started ok and keep reference to pid
            wsl_command = 'wsl -u root bash -c \"' \
                + 'pidof tascar_cli' \
                + '\"'
            try:
                result = subprocess.run(wsl_command,
                                        capture_output=True,
                                        check=True,
                                        text=True)
                self.tascar_pid_as_str = result.stdout.rstrip()
                print('tascar_cli running with pid: ' + self.tascar_pid_as_str)

            except subprocess.CalledProcessError as error:
                print('tascar_cli didn''t start')
                print(wsl_command)
                print(result)
                raise error
            # result = subprocess.check_output(wsl_command)
            # print(result)

            # one shot for the background
            self.video_client.send_message(
                "/video/play", [0, str(self.skybox_absolute_path)])
            self.tascar_client.send_message("/transport/locate", [0.0])
            self.tascar_client.send_message("/transport/start", [])
            self.next_stimulus_index = 0
            self.state = avrc.AVRCState.ACTIVE
        else:
            # TODO: Can we automate progressing through states rather than just
            # falling over?
            raise RuntimeError("Cannot start scene before it has been setup")

    def stop_scene(self):
        # print('Entering stop_scene')
        # print(self.state)
        # print(avrc.AVRCState.ACTIVE)
        if self.state is avrc.AVRCState.ACTIVE:

            # self.tascar_client.send_message("/transport/stop", [])
            # time.sleep(0.2)
            # self.tascar_client.send_message("/transport/unload", [])
            # time.sleep(0.2)
            #
            # # make sure the samplers exit gracefully
            # self.sampler_client1.send_message(
            #     "/" + self.masker1_source_name + "/quit", [])
            # # delattr(self, 'sampler_client1')
            # self.sampler_client2.send_message(
            #     "/" + self.target_source_name + "/quit", [])
            # # delattr(self, 'sampler_client2')
            # self.sampler_client3.send_message(
            #     "/" + self.masker2_source_name + "/quit", [])
            # # delattr(self, 'sampler_client3')

            # end tascar_cli process directly - more graceful than terminating
            # the process in windows land
            wsl_command = 'wsl ' \
                + '-u root bash -c \"kill ' \
                + self.tascar_pid_as_str \
                + '\"'
            # print(wsl_command)
            subprocess.run(wsl_command)
            # print("sent kill signal waiting...")
            # for count_down in [5, 4, 3, 2, 1]:
            #     print(str(count_down))
            #     time.sleep(1)
            # # print(self.tascar_process.poll())
            # print(self.tascar_process)
            if self.tascar_process.poll() is None:
                # print('Calling terminate')
                self.tascar_process.terminate()
                self.state = avrc.AVRCState.TERMINATED


class TargetToneInNoise(ListeningEffortPlayerAndTascarUsingOSCBase):
    """
    Demo to show probe level control without requiring speech files
    """

    # Override constructor to allow settings to be passed in
    def __init__(self, config):
        app_name = 'TargetToneInNoise'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        self.state = avrc.AVRCState.INIT

        # carry on and do the congiguration
        if config is not None:
            self.load_config(config)

    def load_config(self, config):
        # grab the bits we need
        self.data_root_dir = config["root_dir"]
        self.tascar_scn_file = pathlib.Path(self.data_root_dir,
                                            'tascar_scene.tsc')
        check_path_is_file(self.tascar_scn_file)
        self.tascar_scn_file_wsl_path = convert_windows_path_to_wsl(
            self.tascar_scn_file
        )

        self.skybox_absolute_path = pathlib.Path(self.data_root_dir,
                                                 'skybox.mp4')
        check_path_is_file(self.skybox_absolute_path)

        # if we get to here we assume the configuration was successful
        self.state = avrc.AVRCState.CONFIGURED

        # carry on do the setup
        self.setup()

    def setup(self):
        """Inherited public interface for setup"""
        if self.state == avrc.AVRCState.CONFIGURED:
            try:
                self.setup_osc()
            except Exception as err:
                print('Encountered error in setup_osc():')
                print(err)
                print('Perhaps configuration had errors...reload config')
                self.state = avrc.AVRCState.INIT
            else:
                self.state = avrc.AVRCState.READY_TO_START
        else:
            raise RuntimeError('Cannot call setup() before it has been '
                               'configured')

    def set_probe_level(self, probe_level):
        pass

    def present_next_trial(self):
        # unmute target
        self.tascar_client.send_message("/main/target/mute", [0])
        time.sleep(0.5)
        self.tascar_client.send_message("/main/target/mute", [1])


class TargetSpeechTwoMaskers(ListeningEffortPlayerAndTascarUsingOSCBase):
    """
    Demo to show speech probe with point source maskers - all materials
    provided as files which are listed in txt files. Txt files have relative
    paths hard coded into the tascar_scene.tsc file but the location of the
    paths to the data files are absolute so can be anywhere.
    """

    # Override constructor to allow settings to be passed in
    def __init__(self, config):
        app_name = 'TargetSpeechTwoMaskers'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        self.state = avrc.AVRCState.INIT

        # carry on and do the congiguration
        if config is not None:
            self.load_config(config)

    def load_config(self, config):
        # grab the bits we need
        self.data_root_dir = config["root_dir"]

        # tascar scene
        self.tascar_scn_file = pathlib.Path(self.data_root_dir,
                                            'tascar_scene.tsc')
        check_path_is_file(self.tascar_scn_file)
        self.tascar_scn_file_wsl_path = convert_windows_path_to_wsl(
            self.tascar_scn_file)

        # skybox
        self.skybox_absolute_path = pathlib.Path(self.data_root_dir,
                                                 'skybox.mp4')
        check_path_is_file(self.skybox_absolute_path)

        # delay between maskers and target
        self.pre_target_delay = config["pre_target_delay"]
        # TODO: validate

        # read in and validate video list
        self.present_target_video = config["present_target_video"]

        # get the masker directions

        # if we get to here we assume the configuration was successful
        self.state = avrc.AVRCState.CONFIGURED

        # carry on do the setup
        self.setup()

    def setup(self):
        """Inherited public interface for setup"""
        print('Entered setup()')
        if self.state == avrc.AVRCState.CONFIGURED:
            try:
                self.setup_osc()
            except Exception as err:
                print('Encountered error in setup_osc():')
                print(err)
                print('Perhaps configuration had errors...reload config')
                self.state = avrc.AVRCState.INIT

            # continue with setup
            self.target_source_name = 'source2'
            self.masker1_source_name = 'source1'
            self.masker2_source_name = 'source3'
            self.target_linear_gain = 1.0
            self.masker_linear_gain = 1.0

            # TODO: set the positions of the maskers

            # save state
            self.state = avrc.AVRCState.READY_TO_START
        else:
            raise RuntimeError('Cannot call setup() before it has been '
                               'configured')

    def set_probe_level(self, probe_level):
        """Probe level is SNR in dB

        This is interpreted as the relative gain to be applied to the target
        """
        self.target_linear_gain = np.power(10.0, (probe_level/20.0))

    def present_next_trial(self):
        print('Entered present_next_trial() with stimulus: '
              + str(self.next_stimulus_index))

        # start maskers
        msg_address = ("/" + self.masker1_source_name
                       + "/" + str(self.next_stimulus_index+1)
                       + "/add")
        msg_contents = [1, self.masker_linear_gain]  # loop_count, linear_gain
        print(msg_address)
        self.sampler_client1.send_message(msg_address, msg_contents)

        msg_address = ("/" + self.masker2_source_name
                       + "/" + str(self.next_stimulus_index+1)
                       + "/add")
        msg_contents = [1, self.masker_linear_gain]  # loop_count, linear_gain
        print(msg_address)
        self.sampler_client3.send_message(msg_address, msg_contents)

        # pause
        time.sleep(self.pre_target_delay)

        # start target
        if self.present_target_video:
            # self.video_client.send_message()
            pass

        msg_address = ("/" + self.target_source_name
                       + "/" + str(self.next_stimulus_index+1)
                       + "/add")
        msg_contents = [1, self.target_linear_gain]  # loop_count, linear_gain
        print(msg_address + str(msg_contents))
        self.sampler_client2.send_message(msg_address, msg_contents)

        # finally increment counter
        self.next_stimulus_index += 1
