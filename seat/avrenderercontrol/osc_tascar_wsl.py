# from .av_renderer_control import AVRendererControl
import avrenderercontrol.av_renderer_control as avrc
import confuse
import pathlib
import pandas as pd
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
        self.close_osc()
        self.stop_scene()

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

            #
            # TODO: check that the process started ok

            # give tascar a chance to start
            time.sleep(1)

            # one shot for the background
            self.video_client.send_message(
                "/video/play", [0, str(self.skybox_absolute_path)])
            self.tascar_client.send_message("/transport/locate", [0.0])
            self.tascar_client.send_message("/transport/start", [])
            self.nextStimulusIndex = 0
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

            # print(self.tascar_process.poll())
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
