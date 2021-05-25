import argparse
import confuse
import enum
import ipaddress
from pathlib import Path
import psutil
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


class JackTripControl:
    """
    Python interface which wraps scripts to start (TODO: and stop) the jack and
    jacktrip processes
    """
    ready_string = 'Received Connection from Peer!'
    
    # TODO: add state checks for jack and jacktrip processes on local and
    # remote
    def __init__(self, args=None):
        # get default configuration values
        app_name = 'JackTripControl'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        # override with supplied arguments
        if args is not None:
            self.moduleConfig.set_args(args)
        self.ready_string = 'Received Connection from Peer!'
        self.wsl_ip = self.get_wsl_ip_address() 
        self.state = State.DISCONNECTED


    def set_state(self, state):
        self.state = state
        print(f'State set to {self.state}')
        
        
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
        
        # pack into a dict
        cmd_dict = {'wsl_jack': cmd_wsl_jack,
                    'wsl_jacktrip': cmd_wsl_jacktrip,
                    'wsl_kill': cmd_wsl_kill,
                    'local_jack': cmd_local_jack,
                    'local_jacktrip': cmd_local_jacktrip,
                    'local_kill': cmd_local_kill
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
        completed_process = subprocess.run(cmd_dict["wsl_kill"], text=True, capture_output=True)
        completed_process = subprocess.run(cmd_dict["local_kill"], text=True, capture_output=True)
                
    def start(self, raise_error=False, block=True, timeout=30):
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
        # get the commands
        cmd_dict = self.get_commands()
        
        # initialise the objects
        self.lp = dict()
        self.lp["wsl_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jack"])
        self.lp["local_jack"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jack"])
        time.sleep(0.1)
        self.lp["wsl_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["wsl_jacktrip"])
        self.lp["local_jacktrip"] = loggedprocess.LoggedProcess(
            command_string=cmd_dict["local_jacktrip"])
        self.set_state(State.STARTING)
        
        # start each one
        for proc_id, lp in self.lp.items():
            lp.start()
        
        # check they are running
        for proc_id, lp in self.lp.items():
            # print(lp)
            if not lp.is_running():
                self.stop()
                raise RuntimeError(f'{proc_id} process failed to start')
        
        # start thread to connect when ready
        self.t = threading.Thread(target=JackTripControl.connect_when_ready,
                                  args=(self,timeout))
        self.t.start()
        if block:
            print(f'Waiting for thread')
            self.t.join(timeout)
            print(f'Thread joined')
        

    def connect_when_ready(self, timeout):
        # wait for jacktrips to talk to each other
        sleeptime = 0.1
        max_sleeps = timeout/sleeptime
        counter = 0
        while (self.state is State.STARTING) and (counter < max_sleeps):
            time.sleep(sleeptime)
            
            if (self.lp["local_jacktrip"].output_contains(JackTripControl.ready_string)
                and self.lp["wsl_jacktrip"].output_contains(JackTripControl.ready_string)):
                
                # connect jacktrip to soundcard
                # state should be updated
                self.connect_jacktrip_to_output()
                print('Before break')
                break
 
    def stop(self):

        for proc_id, lp in self.lp.items():
            print(lp)
            if lp.is_running():
                lp.stop()
    # def stop(self):
    #     # this check fails if we want to start/stop from
    #     # separate scripts
    #     #if self.isRunning: 
    #         subprocess.run(["powershell.exe", KILL_REMOTE_SCRIPT],
    #                        shell=True,check=True)
            
            
    #         local_process_names = ["jackd.exe"] #only need to kill jack (jacktrip will die anyway)

    #         for proc in psutil.process_iter():
    #             # check whether the process name matches
    #             if proc.name() in local_process_names:
    #                 proc.terminate()

            

    #         time.sleep(1)
    #         for proc in psutil.process_iter():
    #             # check whether the process name matches
    #             if proc.name() in local_process_names:
    #                 proc.kill()
    #         self.isRunning = False




        


    # def disconnect(self):
    #     subprocess.run(["powershell.exe", DISCONNECT_SOUNDCARD_SCRIPT],
    #                    check=True)

    # def test_metronome_manual(self):
    #     subprocess.run(["powershell.exe", TEST_REMOTE_METRONOME_SCRIPT],
    #                    check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--asio_soundcard_name', help='device name used by jack to identify the soundcard')
    args = parser.parse_args()

    jtc = JackTripControl(args)
    jtc.start()
