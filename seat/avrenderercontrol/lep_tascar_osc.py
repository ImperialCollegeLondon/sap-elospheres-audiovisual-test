# from .av_renderer_control import AVRendererControl
import avrenderercontrol.av_renderer_control as avrc
import confuse
import errno
import ipaddress
import numpy as np
import os
import pathlib
from pythonosc import udp_client
import subprocess
import sys
import time
import util

# helper functions
# leading underscore avoids being imported





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


def read_and_validate_paths(file_path):
    """
    Read a text file containing a list of paths and check that each one exists

    Returns a list of paths
    """
    file_path = pathlib.Path(file_path)
    list_of_paths = []
    with open(file_path, 'r') as f:
        for line in f:
            this_path = pathlib.Path(line.rstrip())
            util.check_path_is_file(this_path)
            list_of_paths.append(this_path)
    return list_of_paths


class SourceInterface:

    def __init__(self, config):
        self.video_id = config["video_id"]
        self.video_client = config["video_client"]

        self.sampler_client = config["sampler_client"]
        self.tascar_client = config["tascar_client"]
        self.tascar_source_address = config["tascar_source_address"]


    # def set_position(self, xyz):
    #     pos = np.array(xyz, dtype=np.float32)
    #     # tascar is just the values
    #     msg_address = self.tascar_source_address + '/pos'
    #     print('Setting source postion OSC:' + msg_address + ' ' + str(xyz))
    #     self.tascar_client.send_message(msg_address, xyz)
    #
    #     # unity we only care about the angle
    #     # Euler angles can represent a three dimensional rotation by
    #     # performing three separate rotations around individual axes.
    #     # In Unity these rotations are performed around the Z axis,
    #     # the X axis, and the Y axis, in that order.
    #
    #     # unity x <-> tascar -y
    #     # unity y <-> tascar  z
    #     # unity z <-> tascar  x
    #
    #     # so we can interpret
    #     # rot_X as elevation (90-inclination)
    #     # rot_Y as azimuth
    #     if not (xyz[2]==0):
    #         print('Sources off the horizontal plane are not yet supported!')
    #         raise NotImplementedError()
    #     hypotxy = np.hypot(xyz[0], xyz[1])
    #     r = np.hypot(hypotxy, xyz[2])
    #     unity_Y_deg = -np.rad2deg(np.arctan2(xyz[1], xyz[0]))
    #     unity_X_deg = np.rad2deg(np.arcsin(xyz[2]/r))
    #     print('Unity_Y_deg: ' + str(unity_Y_deg))
    #     print('Unity_X_deg: ' + str(unity_X_deg))
    #     self.video_client.send_message("/video/position",
    #                                    [self.screen_id,
    #                                     unity_X_deg, unity_Y_deg, 0.,
    #                                      self.quad_x_euler,
    #                                      self.quad_y_euler,
    #                                      self.quad_x_scale,
    #                                      self.quad_y_scale
    #                                    ])
    def set_position(self, position):
        """
        Takes a dict of values and deals with sending messages to the appropriate clients.

        Rely on the calling class to figure out what these should be. Either mathematically
        or directly from the config file. For simplicity we assume each value is a single scalar which can be cast to the appropriate format
        key, values:

        numpy array of np.float32 values specifying x,y,z co-ordinates in metres

        tascar:
            x:
            y:
            z:
        unity:
            X_deg:
            Y_deg:
            Z_deg:
            quad_x_euler:
            quad_y_euler:
            quad_x_scale:
            quad_y_scale:


        # unity we only care about the angle
        # Euler angles can represent a three dimensional rotation by
        # performing three separate rotations around individual axes.
        # In Unity these rotations are performed around the Z axis,
        # the X axis, and the Y axis, in that order.

        # unity x <-> tascar -y
        # unity y <-> tascar  z
        # unity z <-> tascar  x

        # so we can interpret
        # rot_X as elevation (90-inclination)
        # rot_Y as azimuth

        """
        print(position)
        # collate the required information
        # - tascar part
        t = position['tascar']
        print(t)
        xyz = [t["x"], t["y"], t["z"]]
        # - unity part
        # u = position['unity']
#         arg = [self.video_id,
#                u.X_deg, u.Y_deg, u.Z_deg,
#                u.quad_x_euler, u.quad_y_euler,
#                u.quad_x_scale, u.quad_y_scale]

        # send the messages
        msg_address = self.tascar_source_address + '/pos'
        self.tascar_client.send_message(msg_address, xyz)
        print('Setting source postion OSC:' + msg_address + ' ' + str(xyz))

        # self.video_client.send_message("/video/position", arg)


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
        print('Running setup_osc()')
        # obtain tascar ipaddress from tascar_cli implementation
        # we don't actually use the tascar_cli to get the ipaddress but
        self.video_client = udp_client.SimpleUDPClient(
            self.moduleConfig['unity']['ipaddress'].get(str),
            self.moduleConfig['unity']['oscport'].get(int))
        self.tascar_client = udp_client.SimpleUDPClient(
            self.tascar_cli.ip_address,
            self.tascar_cli.osc_port)

        for src_name in self.src:
            # this works on MacLocal but not WSL
            # self.src[src_name]["sampler_client"] = udp_client.SimpleUDPClient(
            #     self.src[src_name]["sampler_ip_address"],
            #     self.src[src_name]["sampler_osc_port"])

            # this works on WSL
            self.src[src_name]["sampler_client"] = udp_client.SimpleUDPClient(
                self.tascar_cli.ip_address,
                self.src[src_name]["sampler_osc_port"])

        # tell unity where to send the head rotation data
        self.video_client.send_message("/set_client_address",
            [ self.tascar_cli.ip_address, self.tascar_cli.osc_port ])

        # set the camera rig rotation so that front direction is correct
        # EulerX, EulerY, EulerZ in Unity's left handed, z is depth coordinates
        # self.video_client.send_message("/set_orientation", [0., 90., 0.])
        # self.video_client.send_message("/set_orientation", [0., 0., 0.])
        # self.video_client.send_message("/set_orientation", [0., 180., 0.])

    def close_osc(self):
        # this isn't really necessary but avoids warnings in unittest
        if hasattr(self, 'video_client'):
            self.video_client._sock.close()
        if hasattr(self, 'tascar_client'):
            self.tascar_client._sock.close()
        for src_name in self.src:
            if hasattr(self.src[src_name], 'sampler_client'):
                self.src[src_name].sampler_client._sock.close()

    def start_scene(self):
        """
        Basic implementation - subclasses may need to override
        """
        if self.state == avrc.AVRCState.READY_TO_START:

            self.tascar_cli.start()

            # TODO: abstract the sending of messages for the background
            # one shot for the background
            self.video_client.send_message(
                "/video/play", [0, str(self.skybox_path)])
            self.tascar_client.send_message("/transport/locate", [0.0])
            self.tascar_client.send_message("/transport/start", [])
            self.state = avrc.AVRCState.ACTIVE
        else:
            # TODO: Can we automate progressing through states rather than just
            # falling over?
            raise RuntimeError("Cannot start scene before it has been setup")

    def stop_scene(self):
        if self.state is avrc.AVRCState.ACTIVE:
            self.tascar_cli.stop()
            self.state = avrc.AVRCState.TERMINATED



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
        # TODO: validate, validate, validate !!!

        # instantiate the required type of tascar_cli
        self.tascar_cli = util.instance_builder(config["TascarCommandLineInterface"])

        # skybox
        self.skybox_path = pathlib.Path(config["skybox_path"])
        util.check_path_is_file(self.skybox_path)

        # delay between cue and target
        self.cue_duration = config["cue_duration"]


        self.target_names = config["target_names"]
        self.masker_names = config["masker_names"]

        # read in and validate per source properties
        self.src = {};
        for src_name in config["sources"]:
            # check that src_name is defined as either a masker or target - error if not xor
            if not ((src_name in self.target_names) ^ (src_name in self.masker_names)):
                raise ValueError("Configuration for AVRendererControl must assign each source to be either masker or target")

            self.src[src_name] = {}

            # "present_video" field is used as we may have a video_paths file but choose not to use it.
            if not config["sources"][src_name]["present_video"]:
                self.src[src_name]["video_paths"] = None
            else:
                self.src[src_name]["video_paths"] = read_and_validate_paths(config["sources"][src_name]["video_paths_file"])


            if not config["sources"][src_name]["present_cue_video"]:
                self.src[src_name]["cue_video_paths"] = None
            else:
                self.src[src_name]["cue_video_paths"] = read_and_validate_paths(config["sources"][src_name]["cue_videos_paths_file"])

            # locations are stored as one per line
            if "locations_file" in config["sources"][src_name]:
                with open(config["sources"][src_name]["locations_file"]) as f:
                    self.src[src_name]["locations"] = [line.strip() for line in f]
            else:
                self.src[src_name]["locations"] = None

            # remaining properties are copied in exactly
            for prop_name in ["tascar_scene", "tascar_source",
                              "sampler_ip_address","sampler_osc_port",
                              "video_id"]:
                self.src[src_name][prop_name] = config["sources"][src_name][prop_name]




        self.locations = config["named_locations"]
        # TODO: validation of properties


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
                raise err

            # continue with setup
            self.target_linear_gain = 1.0
            self.masker_linear_gain = 1.0

            # create interface to each source for controlling position
            for src_name in self.src:
                print(self.src[src_name])
                si_config = {
                    "video_id": self.src[src_name]["video_id"],
                    "video_client": self.video_client,
                    "sampler_client": self.src[src_name]["sampler_client"],
                    "tascar_client": self.tascar_client,
                    "tascar_source_address": f'/{self.src[src_name]["tascar_scene"]}/{self.src[src_name]["tascar_source"]}'
                }
                self.src[src_name]["interface"] = SourceInterface( si_config )

            # save state
            self.state = avrc.AVRCState.READY_TO_START
        else:
            raise RuntimeError('Cannot call setup() before it has been '
                               'configured')

    def start_scene(self):
        print('Entered start_scene in child class')
        super().start_scene()
        time.sleep(5)

        # previously set directions of all sources here but should be unnecessary


    def set_probe_level(self, probe_level):
        """Probe level is SNR in dB

        This is interpreted as the relative gain to be applied to the target
        """
        self.target_linear_gain = np.power(10.0, (probe_level/20.0))

    def get_position_from_location(self, location):
        return self.locations[location]

    def present_trial(self, stimulus_id):
        # print('Entered present_trial() with stimulus: ' + str(stimulus_id))

        # set directions of all sources
        for src_name in self.src:
            if self.src[src_name]["locations"] is not None:
                # print(f'setting postion of {src_name}')
                location = self.src[src_name]["locations"][stimulus_id]
                position = self.get_position_from_location(location)
                self.src[src_name]["interface"].set_position(position)

        # present any cues (only videos for now, but could add audio too)
        for src_name in self.src:
            if self.src[src_name]["cue_video_paths"] is not None:
                msg_contents = [
                    self.src[src_name]["video_id"],
                    str(self.src[src_name]["cue_video_paths"][stimulus_id])]
                self.video_client.send_message("/video/play", msg_contents)


        # pause
        time.sleep(self.cue_duration)


        # present stimuli - all videos then all audio
        for src_name in self.src:
            if self.src[src_name]["video_paths"] is not None:
                msg_contents = [
                    self.src[src_name]["video_id"],
                    str(self.src[src_name]["video_paths"][stimulus_id])]
                self.video_client.send_message("/video/play", msg_contents)

        # - audio after a short pause to get lip sync right
        time.sleep(0.15)

        # loop over maskers and target(s) separately to allow for different gains
        for src_name in self.masker_names:
            msg_address = f'/{self.src[src_name]["tascar_source"]}/{stimulus_id+1}/add'
            msg_contents = [1, self.masker_linear_gain]  # loop_count, linear_gain
            print(msg_address)
            self.src[src_name]["sampler_client"].send_message(msg_address, msg_contents)

        for src_name in self.target_names:
            msg_address = f'/{self.src[src_name]["tascar_source"]}/{stimulus_id+1}/add'
            msg_contents = [1, self.target_linear_gain]  # loop_count, linear_gain
            print(msg_address)
            self.src[src_name]["sampler_client"].send_message(msg_address, msg_contents)
