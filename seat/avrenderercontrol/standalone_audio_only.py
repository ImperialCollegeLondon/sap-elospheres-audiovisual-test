# from .av_renderer_control import AVRendererControl
import avrenderercontrol.av_renderer_control as avrc
import confuse
import pathlib
import numpy as np
import ipaddress
import os
import errno
from pythonosc import udp_client
import time
import sounddevices as sd
import subprocess
import sys


class StandaloneAudioOnlyBase(avrc.AVRendererControl):
    """
    Implement common functionality required by renderers operating in standalone mode
    """
    def __init__(self, config):
        app_name = 'StandaloneAudioOnlyAVCR'
        self.moduleConfig = confuse.Configuration(app_name, __name__)


    # implement conext manager magic
    def __enter__(self):
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_scene()


    def load_config(self, config):
        print(f'StandaloneAudioOnlyBase.load_config called by {self.__class__.__name__}')
        self.state = avrc.AVRCState.CONFIGURED

        #TODO: get this from the config
        required_channels = 2

        sd.check_output_settings(device=None, channels=None, dtype=None, extra_settings=None, samplerate=None)
        .query_devices(device=None, kind=None)

        # carry on do the setup
        self.setup()

    def setup(self):
        """Inherited public interface for setup"""
        if self.state == avrc.AVRCState.CONFIGURED:
            try:
                pass
            except Exception as err:
                print('Encountered error in setup')
                print(err)
                print('Perhaps configuration had errors...reload config')
                self.state = avrc.AVRCState.INIT
            else:
                self.state = avrc.AVRCState.READY_TO_START
        else:
            raise RuntimeError('Cannot call setup() before it has been '
                               'configured')

    def set_probe_level(self, probe_level):
        print('Dummy.set_probe_level called')

    def present_trial(self, stimulus_id):
        print('Dummy.present_trial called')


    def start_scene(self):
        """
        Basic implementation - subclasses may need to override
        """
        if self.state == avrc.AVRCState.READY_TO_START:
            self.state = avrc.AVRCState.ACTIVE
        else:
            # TODO: Can we automate progressing through states rather than just
            # falling over?
            raise RuntimeError("Cannot start scene before it has been setup")

    def stop_scene(self):
        if self.state is avrc.AVRCState.ACTIVE:
            self.state = avrc.AVRCState.TERMINATED


class TargetToneInNoise(StandaloneAudioOnlyBase):
    """
    Demo to show probe level control without requiring speech files
    """

    # Override constructor to allow settings to be passed in
    def __init__(self, config):
        super().__init__(config)

        # defaults only
        self.tone_frequency_hz = 1000
        self.noise_type = 'white'
        self.n_output_channels = 2

        self.state = avrc.AVRCState.INIT

        # carry on and do the congiguration
        if config is not None:
            self.load_config(config)

    def load_config(self, config):
        # # grab the bits we need
        # self.tascar_scn_win_path = pathlib.Path(config["tascar_scene_path"])
        # check_path_is_file(self.tascar_scn_win_path)
        # self.tascar_scn_wsl_path = convert_windows_path_to_wsl(
        #     self.tascar_scn_win_path
        # )

        # # skybox
        # self.skybox_path = pathlib.Path(config["skybox_path"])
        # check_path_is_file(self.skybox_path)

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

    def present_trial(self, stimulus_id):
        # unmute target
        self.tascar_client.send_message("/main/target/mute", [0])
        time.sleep(0.5)