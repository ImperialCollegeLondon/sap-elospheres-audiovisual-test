# from .av_renderer_control import AVRendererControl
import avrenderercontrol.av_renderer_control as avrc
import confuse
import pathlib
import pandas as pd
import pprint
import ipaddress
import os
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
            # launch tascar
            subprocess.run([
                "wsl.exe",
                "-u root bash -c "
                "\"tascar_cli demo_data/tascar_scenes/00_binaural_demo.tsc\""
                ])

            # one shot for the background
            self.video_client.send_message(
                "/video/play", [0, self.skybox_absolute_path])
            self.tascar_client.send_message("/transport/locate", [0.0])
            self.tascar_client.send_message("/transport/start", [])
            self.nextStimulusIndex = 0
            self.state = avrc.AVRCState.ACTIVE
        else:
            # TODO: Can we automate progressing through states rather than just
            # falling over?
            raise RuntimeError("Cannot start scene before it has been setup")


class TargetToneInNoise(ListeningEffortPlayerAndTascarUsingOSCBase):
    """
    Demo to show probe level control without requiring speech files
    """

    # Override constructor to get the right config settings
    def __init__(self):
        # get the IP addresses
        app_name = 'TargetToneInNoise'
        self.moduleConfig = confuse.Configuration(app_name, __name__)

    def load_config(self, config):
        # grab the bits we need
        # - blocks are presented in order
        block_config = config["blocks"][
            config["state_control"]["current_block_index"].get(int)
            ]
        pprint.pprint(block_config.get)

        # - pandas dataframe from list of dicts makes it easy to find the right
        #   listening condition
        pprint.pprint(config["listening_conditions"].get())
        df = pd.DataFrame(config["listening_conditions"].get())
        matching_index = df[
            df["id"] == block_config["listening_condition_id"].get(str)
            ].index.values
        num_of_matches = len(matching_index)
        assert num_of_matches == 1, \
            "expected one match but got {}".format(num_of_matches)
        lc_config = config["listening_conditions"][matching_index[0]]
        pprint.pprint(lc_config.get)

        # get the fully qualified path to the skybox video in stages
        skybox_dir = self.skybox = pathlib.Path(
            config["paths"]["unity_data"]["root_dir"].get(str),
            config["paths"]["unity_data"]["skybox_rel_dir"].get(str)
            )
        skybox_filename = lc_config["avrenderer"]["skybox_file"].get(str)
        self.skybox_absolute_path = pathlib.Path(skybox_dir, skybox_filename)

        self.state = avrc.AVRCState.CONFIGURED

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
                avrc.AVRCState.READY_TO_START
        else:
            raise RuntimeError('Cannot call setup() before it has been '
                               'configured')

    def set_probe_level(self, probe_level):
        pass

    def present_next_trial(self):
        # unmute target
        self.tascar_client.send_message(["/main/target/mute", [0]])
        time.sleep(1.0)
        self.tascar_client.send_message(["/main/target/mute", [1]])
