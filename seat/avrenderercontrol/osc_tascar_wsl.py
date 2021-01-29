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


class SourceInterface:
    
    
    def __init__(self, video_client=None, sampler_client=None,
                 tascar_client=None, screen_id=None,
                 tascar_source_address=None):
        self.video_client = video_client
        self.screen_id = screen_id
        self.sampler_client = sampler_client
        self.tascar_client = tascar_client
        self.tascar_source_address = tascar_source_address
        
        # Unity local transform on screens, in unity's coordinates
        self.quad_x_euler = 0.
        self.quad_y_euler = 0.
        self.quad_x_scale = 167.
        self.quad_y_scale = 97.
        
    def set_position(self, xyz):
        pos = np.array(xyz, dtype=np.float32)
        # tascar is just the values
        self.tascar_client.send_message(
            self.tascar_source_address + '/pos', xyz)
        
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
        if not (xyz[2]==0):
            print('Sources off the horizontal plane are not yet supported!')
            raise NotImplementedError()
        hypotxy = np.hypot(xyz[0], xyz[1])
        r = np.hypot(hypotxy, xyz[2])
        unity_Y_deg = -np.rad2deg(np.arctan2(xyz[1], xyz[0]))
        unity_X_deg = np.rad2deg(np.arcsin(xyz[2]/r))
        print('Unity_Y_deg: ' + str(unity_Y_deg))
        print('Unity_X_deg: ' + str(unity_X_deg))
        self.video_client.send_message("/video/position",
                                       [self.screen_id,
                                        unity_X_deg, unity_Y_deg, 0.,
                                         self.quad_x_euler,
                                         self.quad_y_euler,
                                         self.quad_x_scale,
                                         self.quad_y_scale
                                       ])


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
        
        # set the camera rig rotation so that front direction is correct
        # EulerX, EulerY, EulerZ in Unity's left handed, z is depth coordinates
        # self.video_client.send_message("/set_orientation", [0., 90., 0.])
        self.video_client.send_message("/set_orientation", [0., 0., 0.])
        
        

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
                + str(self.tascar_scn_wsl_path) \
                + '\"'
            # print(wsl_command)
            self.tascar_process = subprocess.Popen(
                wsl_command, creationflags=subprocess.CREATE_NEW_CONSOLE)

            # give tascar a chance to start
            time.sleep(0.3)

            # check process is running
            if self.tascar_process.poll() is not None:
                # oh dear, it's not running!
                # try again with settings which will allow us to debug
                self.tascar_process = subprocess.Popen(
                    wsl_command, creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                    text=True)
                outs, errs = self.tascar_process.communicate()
                print('stdout:')
                if outs is not None:
                    print(outs)
                    # for line in outs:
                    #     print(line)
                print('stderr:')
                if errs is not None:
                    print(errs)

            # get the process pid in wsl land
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

            except subprocess.CalledProcessError:
                # we got an error, which means we couldn't get the pid
                # nothing to be done but exit gracefully
                print('couldn''t get pid of tascar_cli')
                sys.exit("probably tascar_cli failed to start")

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
            # end tascar_cli process directly using linux kill
            # this avoids audio glitches
            wsl_command = 'wsl ' \
                + '-u root bash -c \"kill ' \
                + self.tascar_pid_as_str \
                + '\"'
            # print(wsl_command)
            subprocess.run(wsl_command)

            # make sure it really has finished
            if self.tascar_process.poll() is None:
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
        self.tascar_scn_win_path = pathlib.Path(config["tascar_scene_path"])
        check_path_is_file(self.tascar_scn_win_path)
        self.tascar_scn_wsl_path = convert_windows_path_to_wsl(
            self.tascar_scn_win_path
        )

        # skybox
        self.skybox_path = pathlib.Path(config["skybox_path"])
        check_path_is_file(self.skybox_path)

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
        self.tascar_scn_win_path = pathlib.Path(config["tascar_scene_path"])
        check_path_is_file(self.tascar_scn_win_path)
        self.tascar_scn_wsl_path = convert_windows_path_to_wsl(
            self.tascar_scn_win_path
        )

        # skybox
        self.skybox_path = pathlib.Path(config["skybox_path"])
        check_path_is_file(self.skybox_path)

        # delay between maskers and target
        self.pre_target_delay = config["pre_target_delay"]
        # TODO: validate

        # read in and validate video list
        self.present_target_video = config["present_target_video"]
        if self.present_target_video:
            self.target_video_paths = []
            with open(pathlib.Path(config["target_video_list_path"]), 'r') \
                    as f:
                for line in f:
                    video_path = pathlib.Path(line.rstrip())
                    check_path_is_file(video_path)
                    self.target_video_paths.append(video_path)


        # assume colocated sources, 2 m in front of listener
        self.target_position = [2., 0., 0.]
        self.masker1_position = [2., 0., 0.]
        self.masker2_position = [2., 0., 0.]

        if "target_position" in config:
            self.target_position = config["target_position"]
        if "masker2_position" in config:
            self.masker1_position = config["masker1_position"]
        if "masker1_position" in config:
            self.masker2_position = config["masker2_position"]    


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
            self.scene_name = 'point_sources'
            self.target_source_name = 'source2'
            self.masker1_source_name = 'source1'
            self.masker2_source_name = 'source3'
            self.target_linear_gain = 1.0
            self.masker_linear_gain = 1.0

            # create interfaces to sources
            self.target_interface = SourceInterface(
                video_client=self.video_client,
                screen_id=2,
                sampler_client=self.sampler_client2,
                tascar_client=self.tascar_client,
                tascar_source_address= ('/' + self.scene_name +
                                       '/'+self.target_source_name)
                )
            
            self.masker1_interface = SourceInterface(
                video_client=self.video_client,
                screen_id=1,
                sampler_client=self.sampler_client1,
                tascar_client=self.tascar_client,
                tascar_source_address= ('/' + self.scene_name +
                                       '/'+self.masker1_source_name))
            self.masker2_interface = SourceInterface(
                video_client=self.video_client,
                screen_id=3,
                sampler_client=self.sampler_client3,
                tascar_client=self.tascar_client,
                tascar_source_address= ('/' + self.scene_name +
                                       '/'+self.masker2_source_name))
            
            # set directions
            print('Setting target postion ' + str(self.target_position))
            self.target_interface.set_position(self.target_position)
            self.masker1_interface.set_position(self.masker1_position)
            self.masker2_interface.set_position(self.masker2_position)
            
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

    def present_trial(self, stimulus_id):
        # print('Entered present_trial() with stimulus: ' + str(stimulus_id))

        # start maskers
        msg_address = ("/" + self.masker1_source_name
                       + "/" + str(stimulus_id+1)
                       + "/add")
        msg_contents = [1, self.masker_linear_gain]  # loop_count, linear_gain
        # print(msg_address)
        self.sampler_client1.send_message(msg_address, msg_contents)

        msg_address = ("/" + self.masker2_source_name
                       + "/" + str(stimulus_id+1)
                       + "/add")
        msg_contents = [1, self.masker_linear_gain]  # loop_count, linear_gain
        # print(msg_address)
        self.sampler_client3.send_message(msg_address, msg_contents)

        # pause
        time.sleep(self.pre_target_delay)

        # start target
        # - video first
        if self.present_target_video:
            # msg_contents = [video player id, video file]
            msg_contents = [2, str(self.target_video_paths[stimulus_id])]
            self.video_client.send_message("/video/play", msg_contents)

        msg_address = ("/" + self.target_source_name
                       + "/" + str(stimulus_id+1)
                       + "/add")
        # - audio after a short pause to get lip sync right
        time.sleep(0.15)
        msg_contents = [1, self.target_linear_gain]  # loop_count, linear_gain
        # print(msg_address + str(msg_contents))
        self.sampler_client2.send_message(msg_address, msg_contents)

    
            