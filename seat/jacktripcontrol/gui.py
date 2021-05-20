import argparse
from datetime import datetime
import ipaddress
import numpy as np
import os
import PySimpleGUI as sg
import subprocess
import sys
import time

from loggedprocess import TabbedProcess




class Gui():
    def __init__(self):
        
        self.key_timeout = '--timeout--'
        self.key_run_button = '--run--'
        self.key_kill_button = '--kill--'
        self.ip = self.get_wsl_ip_address()
        
        buffer_size = 128
        sample_rate = 48000
        local_jack_exe = 'C:/Program Files (x86)/Jack/jackd.exe'
        self.local_jackconnec_exe = 'C:/Program Files (x86)/Jack/jack_connect.exe'
        portaudio_soundcard_name = 'ASIO::Soundcraft USB Audio ASIO'
        local_jacktrip_exe = 'C:\jacktrip_v1.2.1\jacktrip.exe'
        
        cmd_wsl_jack = f'wsl -u root jackd -d dummy -r {sample_rate} -p {buffer_size}'
        cmd_local_jack = f'{local_jack_exe} -S -dportaudio -d\"{portaudio_soundcard_name}\" -r{sample_rate} -p{buffer_size}'
        kill_cmd_local_jack = ''
        # print(cmd_local_jack)
        # cmd_local_jack = 'C:/Program Files (x86)/Jack/jackd.exe -S -dportaudio -d\"ASIO::Soundcraft USB Audio ASIO\" -r48000 -p128'
        # print(cmd_local_jack)

        cmd_wsl_jacktrip = 'wsl -u root jacktrip -s --nojackportsconnect'
        cmd_local_jacktrip = f'{local_jacktrip_exe} -c {self.ip} --clientname {self.ip} --nojackportsconnect'
        
        kill_wsl_jack = 'wsl -u root pkill -f jackd'
        
        # generate the tabs
        # tabs = [TabbedProcess(f'tab_{i}', f'python count.py --step {i}')
        #           for i in range(1,num_tabs+1)]
        # self.tabs = [loggedprocess.TabbedProcess('wsl jack', cmd_wsl_jack),
        #               loggedprocess.TabbedProcess('local jack', cmd_local_jack),
        #               loggedprocess.TabbedProcess('wsl jacktrip', cmd_wsl_jacktrip),
        #               loggedprocess.TabbedProcess('local jacktrip', cmd_local_jacktrip)]
        
        # # debugging only local
        # self.tabs = [loggedprocess.TabbedProcess('local jack', cmd_local_jack,
        #                                          kill_cmd=kill_cmd_local_jack),
        #              loggedprocess.TabbedProcess('local jacktrip', cmd_local_jacktrip)]
               
        # # debugging only wsl
        # self.tabs = [loggedprocess.TabbedProcess('wsl jack', cmd_wsl_jack),
        #              loggedprocess.TabbedProcess('wsl jacktrip', cmd_wsl_jacktrip)]
        # layout = [[sg.TabGroup([[sg.Tab(tab.key, tab.layout) for tab in self.tabs]])],
        #           [sg.Button('Start', key=self.key_run_button),
        #            sg.Button('Stop', key=self.key_kill_button)]]
        
        self.pr_wsl_jack = TabbedProcess('wsl jack', cmd_wsl_jack)
        self.pr_wsl_jt = TabbedProcess('wsl jacktrip', cmd_wsl_jacktrip)
        self.pr_local_jack = TabbedProcess('local jack', cmd_local_jack)
        self.pr_local_jt = TabbedProcess('local jacktrip', cmd_local_jacktrip)
        self.tabs = [self.pr_wsl_jack, self.pr_wsl_jt,
                     self.pr_local_jack, self.pr_local_jt]
        
        layout = [[sg.TabGroup([[sg.Tab(tab.key, tab.layout) for tab in self.tabs]])],
                  [sg.Button('Start', key=self.key_run_button),
                   sg.Button('Stop', key=self.key_kill_button)]]            

        self.window = sg.Window('Window with tabs', layout, finalize=True)
        

        self.ready_string = 'Received Connection from Peer!'
        self.reset()
        
    def reset(self):
        self.stopped = True
        self.waiting = False
        self.running = False

        
    def monitor(self):
        while True:             # Event Loop
            event, values = self.window.Read(timeout=50,timeout_key=self.key_timeout)
            if event is not self.key_timeout:
                # print(event, values)
                pass
            if event == sg.WIN_CLOSED:
                self.window.close()
                return
            elif event == self.key_run_button:
                # stop before we start
                if self.waiting or self.running:
                    for tab in self.tabs:
                        if tab.is_running():
                            tab.stop()
                    self.reset()        
                
                for tab in self.tabs:
                    tab.start(self.window)
                self.stopped = False
                self.waiting = True
                
            elif event == self.key_kill_button:
                for tab in self.tabs:
                    tab.stop()
                self.reset()
                
            # update display on every loop
            for tab in self.tabs:
                tab.update(self.window)

            # update status
            if self.waiting:
                if (self.pr_local_jt.output_contains(self.window, self.ready_string) and
                    self.pr_wsl_jt.output_contains(self.window, self.ready_string)):

                    # connect jacktrip to soundcard
                    self.connect_jacktrip_to_output()
                    self.waiting = False
                    self.running = True
                
                
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
        return str(parsed_address)

    def connect_jacktrip_to_output(self, channels=[1,2]):
        for channel in channels:
            cmd = f'{self.local_jackconnec_exe} {self.ip}:receive_{channel} system:playback_{channel}'
            completed_process = subprocess.run(cmd, text=True, capture_output=True)

    
if __name__ == '__main__':
    thegui = Gui()
    thegui.monitor()
    

    