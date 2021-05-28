import argparse
import confuse
import enum
import ipaddress
import subprocess
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
        self.state = State.DISCONNECTED
        self.initialise_loggedprocesses()
        


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
        cmd_wsl_jack = f'wsl -u root jackd -d dummy -r {sample_rate} -p {buffer_size}'
        cmd_wsl_jacktrip = 'wsl -u root jacktrip -s --nojackportsconnect'
        cmd_wsl_kill = 'wsl -u root pkill -f jackd'
        cmd_local_jack = (f'{jack_root}/jackd.exe -S ' +
                          f'-dportaudio -d\"{asio_soundcard_name}\" ' + 
                          f'-r{sample_rate} -p{buffer_size}')
        cmd_local_jacktrip = (f'{jacktrip_root}/jacktrip.exe -c {self.wsl_ip} ' +
                              f'--clientname {self.wsl_ip} --nojackportsconnect')
        cmd_local_kill = 'taskkill /F /IM jackd.exe /IM jacktrip.exe'
        cmd_start_metronome = 'wsl -u root jack_metro --bpm 100'
        cmd_connect_metronome = f'wsl -u root bash -c "jack_connect metro:100_bpm JackTrip:send_1"'        
        cmd_stop_metronome = f'wsl -u root bash -c "jack_disconnect metro:100_bpm JackTrip:send_1; pkill -9 -f jack_metro"'
        
        # pack into a dict
        cmd_dict = {'wsl_jack': cmd_wsl_jack,
                    'wsl_jacktrip': cmd_wsl_jacktrip,
                    'wsl_kill': cmd_wsl_kill,
                    'local_jack': cmd_local_jack,
                    'local_jacktrip': cmd_local_jacktrip,
                    'local_kill': cmd_local_kill,
                    'wsl_metro_start': cmd_start_metronome,
                    'wsl_metro_connect': cmd_connect_metronome,
                    'wsl_metro_stop': cmd_stop_metronome
                    }
        return cmd_dict


    def initialise_loggedprocesses(self):
        if self.state is not State.DISCONNECTED:
            raise RuntimeError('Cannot call initialise_loggedprocesses unless state is {State.DISCONNECTED}')

        # get the commands
        cmd_dict = self.get_commands()
        
        # initialise the objects
        self.lp_local = dict()
        self.lp_wsl = dict()
        
        # initialise the objects
        self.lp_local["local_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jack"])
        self.lp_wsl["wsl_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jack"])
        self.lp_local["local_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jacktrip"])
        self.lp_wsl["wsl_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jacktrip"])
        
        # keep a dict contain all logged processes
        self.lp_all = {**self.lp_local, **self.lp_wsl}

        # print(f'In initialise_loggedprocesses')
        # for key,lp in self.lp_all.items():
        #     print(f'{key}: {lp.command_string}')

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
        completed_process = subprocess.run(cmd_dict["wsl_kill"], text=True, capture_output=True)
        completed_process = subprocess.run(cmd_dict["local_kill"], text=True, capture_output=True)
        self.set_state(State.DISCONNECTED)
                
    def start(self, raise_error=False, connect_mode=ConnectMode.BLOCKING,
              timeout=maximum_wait_time):
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
        
        # start each one
        # - concatonate dicts and iterate over items
        for proc_id, lp in self.lp_all.items():
            # print(f'Starting {proc_id}...')
            lp.start()
        
        # check they are running
        for proc_id, lp in self.lp_all.items():
            # print(f'checking {lp} started...')
            if not lp.is_running():
                self.stop()
                raise RuntimeError(f'{proc_id} process failed to start')
        
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
            if (self.lp_local["local_jacktrip"].output_contains(JackTripControl.ready_string)
                and self.lp_wsl["wsl_jacktrip"].output_contains(JackTripControl.ready_string)):
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
        for proc_id, lp in self.lp_local.items():
            # print(lp)
            if lp.is_running():
                # print(f'Calling .stop() on {proc_id}')
                lp.stop()
                
        # wsl processes need to be ended explicitly
        cmd_dict = self.get_commands()
        completed_process = subprocess.run(cmd_dict["wsl_kill"], text=True, capture_output=True)
        self.set_state(State.DISCONNECTED)
        
        
    def test_metronome_manual(self):
        """
        Start a metronome playing, wait for user confirmation then stop it

        Returns
        -------
        None.

        """
        cmd_dict = self.get_commands()
        lp = loggedprocess.LoggedProcess(command_string=cmd_dict["wsl_metro_start"])
        lp.start()
        time.sleep(0.1)
        completed_process = subprocess.run(cmd_dict["wsl_metro_connect"], text=True, capture_output=True)
        input('Confirm that the metronome is playing on the left channel (channel 1)')
        completed_process = subprocess.run(cmd_dict["wsl_metro_stop"], text=True, capture_output=True)
 