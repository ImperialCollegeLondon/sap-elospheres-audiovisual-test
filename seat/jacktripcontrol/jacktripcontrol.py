import argparse
import confuse
import enum
import ipaddress
import os
import pathlib
import subprocess
import sys
import threading
import time

import loggedprocess


class State(enum.Enum):
    DISCONNECTED = enum.auto()
    STARTING = enum.auto()
    CONNECTED = enum.auto()
    
    def __str__(self):
        strings = {self.DISCONNECTED.value: 'Disconnected',
                   self.STARTING.value: 'Starting',
                   self.CONNECTED.value: 'Connected'}
        return strings[self.value]

class ConnectMode(enum.Enum):
    NO_CONNECT = enum.auto()
    NON_BLOCKING = enum.auto()
    BLOCKING = enum.auto()


class JTCArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--jack_root', help='Path to folder where jackd.exe is located')
        self.add_argument('--jacktrip_root', help='Path to folder where jacktrip.exe is located')        
        self.add_argument('-r', '--sample_rate', help='Sample rate in Hz')
        self.add_argument('-p', '--buffer_size', help='Number of samples (period) of jack buffer')
        self.add_argument('-d', '--asio_soundcard_name', help='Device name used by jack to identify the soundcard')



class JackTripControl:
    """
    Python interface which wraps scripts to start (TODO: and stop) the jack and
    jacktrip processes
    """
    ready_string = 'Received Connection from Peer!'
    maximum_wait_time = 30
    
    # TODO: add state checks for jack and jacktrip processes on local and
    # remote
    def __init__(self, args=None):
        # get default configuration values
        app_name = 'JackTripControl'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        # override with supplied arguments
        if args is not None:
            self.moduleConfig.set_args(args)
        self.wsl_ip = self.get_wsl_ip_address()
        self.lp = None
        self.state = State.DISCONNECTED
        
        # for seat, we need to know the IP address. Storing it as an
        # environment variable was quite unreliable so instead store it in a
        # file pointed to by an environment variable
        
        env_var_name ='JTC_REMOTE_IP_SETTING'
        # default_remote_ip_file = pathlib.Path(self.moduleConfig.config_dir(),
        #                                   'remote_ip')
        if env_var_name not in os.environ:
            print(os.environ)
            print(f'Environment variable {env_var_name} is missing.')
            print(f'Initialising now')
            self.init_env_variable()
            print(f'Done. Please close the terminal (all tabs)and try again')
            # # choose it and set env variable
            # remote_ip_file = default_remote_ip_file
            # # os.environ[env_var_name] = str(remote_ip_file)
            # # os.system("setx " + str(env_var_name) + " " + str(remote_ip_file))
            sys.exit(-1)
        else:
            remote_ip_file = os.environ.get(env_var_name,'')
            print(f'environment variable: {env_var_name} is\n{remote_ip_file}')
            if remote_ip_file == '':
                raise RuntimeError('Environment variable was empty')
                # env variable exists but its not set
                # remote_ip_file = default_remote_ip_file
                # os.environ[env_var_name] = str(remote_ip_file)
                # os.system("setx " + str(env_var_name) + " " + str(remote_ip_file))
        with open(remote_ip_file,'w') as f:
            print(f'Writing {self.wsl_ip} to {remote_ip_file}')
            f.write(str(self.wsl_ip))
        

    def init_env_variable(self):
        """
        Runs powershell script to setup environment variable - native Python 
        commands don't seem to be persistent

        Returns
        -------
        None.

        """
        module_path = pathlib.Path(__file__).parent.absolute()
        ps_script = pathlib.Path(module_path,'init_env.ps1')
        cmd_str = f'powershell.exe {str(ps_script)}'
        split_cmd = loggedprocess.cmdline_split(cmd_str)
        completed_process = subprocess.run(split_cmd, text=True, capture_output=True)
        

    def set_state(self, state):
        self.state = state
        # print(f'State set to {self.state}')
        
        
    def get_commands(self):
        """
        parse the settings to create a dict of commands


        Returns
        -------
        cmd_dict : dict
            named commands which can be passed to subprocess

        """
        # extract settings
        cfg = self.moduleConfig # for clearer code
        
        # print(f'In jct.get_commands, cfg: \n {cfg}')
        # print(cfg.__dict__)
        jack_root = cfg['jack_root'].as_filename()
        jacktrip_root = cfg['jacktrip_root'].as_filename()
        sample_rate = cfg['sample_rate'].get(int)
        buffer_size = cfg['buffer_size'].get(int)
        asio_soundcard_name = cfg['asio_soundcard_name'].get(str)
        
        # construct commands
        start_wsl_jack = f'wsl -u root jackd -d dummy -r {sample_rate} -p {buffer_size}'
        kill_wsl_jack = 'wsl -u root pkill -f jackd'
        start_wsl_jacktrip = 'wsl -u root jacktrip -s --nojackportsconnect'
        kill_wsl_jacktrip = 'wsl -u root pkill -f jacktrip'
        
        start_local_jack = (f'{jack_root}/jackd.exe -S ' +
                          f'-dportaudio -d\"{asio_soundcard_name}\" ' + 
                          f'-r{sample_rate} -p{buffer_size}')
        kill_local_jack = 'taskkill /F /IM jackd.exe'        
        start_local_jacktrip = (f'{jacktrip_root}/jacktrip.exe -c {self.wsl_ip} ' +
                              f'--clientname {self.wsl_ip} --nojackportsconnect')
        kill_local_jacktrip = 'taskkill /F /IM jacktrip.exe'
        
        
        # pack into a dict
        cmd_dict = {'wsl_jack': {'start': start_wsl_jack,
                                 'kill': kill_wsl_jack},
                    'wsl_jacktrip': {'start': start_wsl_jacktrip,
                                     'kill': kill_wsl_jacktrip},
                    'local_jack': {'start': start_local_jack,
                                   'kill': kill_local_jack},
                    'local_jacktrip': {'start': start_local_jacktrip,
                                       'kill': kill_local_jacktrip},
                    }
        return cmd_dict



    def get_wsl_ip_address(self, verbose=False):
        cmd = 'wsl hostname -I'
        completed_process = subprocess.run(cmd, text=True, capture_output=True)
        ip = completed_process.stdout.rstrip()
    
        try:
            parsed_address = ipaddress.ip_address(ip)
            if verbose:
                print(f'parsed address: {str(parsed_address)}')
        except ValueError as err:
            print(err)
            print(f'invalid address: {ip}')
            raise RuntimeError('Failed to get IP address of WSL virtual machine')
        return parsed_address


    def connect_jacktrip_to_output(self, channels=[1,2]):
        jack_root = self.moduleConfig['jack_root'].as_filename()
        for channel in channels:
            cmd = f'{jack_root}/jack_connect.exe {self.wsl_ip}:receive_{channel} system:playback_{channel}'
            completed_process = subprocess.run(cmd, text=True, capture_output=True)
        # assume success - TODO: check for success
        self.set_state(State.CONNECTED)

    def kill(self):
        """
        Send kill signals to all jack and jacktrip processes running on windows
        and wsl.
        """
        # get the commands
        cmd_dict = self.get_commands()
        
        # be brutal
        completed_process = subprocess.run(cmd_dict["wsl_jacktrip"]["kill"], text=True, capture_output=True)
        completed_process = subprocess.run(cmd_dict["local_jacktrip"]["kill"], text=True, capture_output=True)
        completed_process = subprocess.run(cmd_dict["wsl_jack"]["kill"], text=True, capture_output=True)
        completed_process = subprocess.run(cmd_dict["local_jack"]["kill"], text=True, capture_output=True)
        self.set_state(State.DISCONNECTED)

        
    def start(self, raise_error=False, connect_mode=ConnectMode.BLOCKING,
              timeout=maximum_wait_time, daemon=False):
        """
        start
        Establishes

        Returns
        -------
        None.

        """
        if self.state is not State.DISCONNECTED:
            msg = f'jacktripcontol.start() cannot be called when state is {self.state}'
            if raise_error:
                raise ValueError(msg)
            else:
                print(msg)
                return


        self.set_state(State.STARTING)
        

        # get the commands
        cmd_dict = self.get_commands()
        
        # start the subprocesses
        self.lp = dict()
        self.lp["local_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jack"]["start"],
            detach_on_exit=daemon)
        self.lp["local_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jacktrip"]["start"],
            detach_on_exit=daemon)        
        self.lp["wsl_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jack"]["start"],
            stop_command_string=cmd_dict["wsl_jack"]["kill"],
            detach_on_exit=daemon)
        self.lp["wsl_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jacktrip"]["start"],
            stop_command_string=cmd_dict["wsl_jacktrip"]["kill"],
            detach_on_exit=daemon)
        
        
        # # check they are running
        # for proc_id, lp in self.lp.items():
        #     # print(f'checking {lp} started...')
        #     if not lp.is_running():
        #         self.stop()
        #         raise RuntimeError(f'{proc_id} process failed to start')
        
        # start thread to connect when ready
        if connect_mode is not ConnectMode.NO_CONNECT:
            self.t = threading.Thread(target=JackTripControl.connect_when_ready,
                                  args=(self,timeout))
            # print('Starting connect_when_ready thread')
            self.t.start()
            if connect_mode is ConnectMode.BLOCKING:
                # print(f'Waiting for JackTrip to connect')
                self.t.join(timeout)
                # print(f'Thread joined')
                # finished waiting
                if self.t.is_alive():
                    # thread hasn't finished so need to give up
                    # set state to break loop in thread
                    self.set_state(State.DISCONNECTED)
                
        

    def connect_when_ready(self, timeout):
        # wait for jacktrips to talk to each other
        sleeptime = 0.1
        max_sleeps = timeout/sleeptime
        # print(f'max_sleeps: {max_sleeps}')
        counter = 0
        while (self.state is State.STARTING) and (counter < max_sleeps):
            counter+=1
            time.sleep(sleeptime)
            # print(f'checking if ready - {counter} of {max_sleeps}')
            if (self.lp["local_jacktrip"].output_contains(JackTripControl.ready_string)
                and self.lp["wsl_jacktrip"].output_contains(JackTripControl.ready_string)):
                # print('ready to connect')
                # connect jacktrip to soundcard
                # state should be updated
                self.connect_jacktrip_to_output()
                # print('successful connection')
                break
        # dropped out of loop
        if self.state is not State.CONNECTED:
            #  didn't work so tear it down
            self.kill()
 
    def stop(self):
        # all processes need stop() to be called to make their threads exit 
        # local processes can be stopped nicely using the proc object
        for proc_id, lp in self.lp.items():
            lp.stop()
                
        self.set_state(State.DISCONNECTED)
        
        
    def test_metronome_manual(self):
        """
        Start a metronome playing, wait for user confirmation then stop it

        Returns
        -------
        None.

        """
        start_metronome = 'wsl -u root jack_metro --bpm 100'
        connect_metronome = f'wsl -u root bash -c "jack_connect metro:100_bpm JackTrip:send_1"'        
        kill_metronome = f'wsl -u root bash -c "jack_disconnect metro:100_bpm JackTrip:send_1; pkill -9 -f jack_metro"'

        
        cmd_dict = self.get_commands()
        lp = loggedprocess.LoggedProcess(command_string=start_metronome)
        time.sleep(0.1)
        completed_process = subprocess.run(connect_metronome, text=True, capture_output=True)
        input('Confirm that the metronome is playing on the left channel (channel 1)')
        completed_process = subprocess.run(kill_metronome, text=True, capture_output=True)
 