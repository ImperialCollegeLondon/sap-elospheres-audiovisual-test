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
import subprocess
import sys


class Dummy(avrc.AVRendererControl):
    """
    Class to satisfy requirements of the abstract base class
    """
    def __init__(self, config):
        # app_name = 'DummyAVRC'
      #   self.moduleConfig = confuse.Configuration(app_name, __name__)
        self.state = avrc.AVRCState.INIT
        #
        # # carry on and do the congiguration
        if config is not None:
            self.load_config(config)
        # self.state = avrc.AVRCState.INIT

    # implement conext manager magic
    def __enter__(self):
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_scene()


    def load_config(self, config):
        print('Dummy.load_config called')
        self.state = avrc.AVRCState.CONFIGURED

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


