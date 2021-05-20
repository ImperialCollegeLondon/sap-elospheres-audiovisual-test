import argparse
import confuse
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
    def __init__(self, args):
        # get default configuration values
        app_name = 'JackTripControl'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        # override with command line arguments
        self.moduleConfig.set_args(args)
        
        # use the config values to populate values in the UI but don't override
        # the config structure itself
        
        
        
        self.key_timeout = '--timeout--'
        self.key_top_tabgroup = '--tabgroup--'
        self.key_reset_settings_button = '--reset-settings--'
        self.key_run_button = '--run--'
        self.key_kill_button = '--kill--'
        self.settings_map = {'jack_root': {'ui_key': 'jack_root',
                                           'label': 'Root directory for Jack',
                                           'value': self.moduleConfig['jack_root'].as_filename()},
                             'jacktrip_root': {'ui_key': 'jacktrip_root',
                                           'label': 'Root directory for JackTrip',
                                           'value': self.moduleConfig['jacktrip_root'].as_filename()},
                             'sample_rate': {'ui_key': 'sample_rate',
                                           'label': 'Sample rate [Hz]',
                                           'value': str(self.moduleConfig['sample_rate'].get(int))},
                             'buffer_size': {'ui_key': 'buffer_size',
                                           'label': 'Buffer size [samples]',
                                           'value': str(self.moduleConfig['buffer_size'].get(int))},
                             'asio_soundcard_name': {'ui_key': 'asio_soundcard_name',
                                           'label': 'ASIO sound card name (as reported by portaudio)',
                                           'value': self.moduleConfig['asio_soundcard_name'].get(str)}
                             }
        self.ready_string = 'Received Connection from Peer!'
        self.ip = self.get_wsl_ip_address()
            
        
        # create elements with dummy text for now
        self.pr_wsl_jack = TabbedProcess('wsl jack', 'cmd_wsl_jack', read_only=True)
        self.pr_wsl_jt = TabbedProcess('wsl jacktrip', 'cmd_wsl_jacktrip', read_only=True)
        self.pr_local_jack = TabbedProcess('local jack', 'cmd_local_jack', read_only=True)
        self.pr_local_jt = TabbedProcess('local jacktrip', 'cmd_local_jacktrip', read_only=True)
        self.console_tabs = [self.pr_wsl_jack, self.pr_wsl_jt,
                     self.pr_local_jack, self.pr_local_jt]
        print('console group')
        console_tab_group = [[sg.TabGroup([[sg.Tab(tab.key, tab.layout) for tab in self.console_tabs]])]]

        main_tab_layout = [[sg.Text(text='This is the main tab. We will write something here soon')]]

        settings_tab_layout = [[]]
        for key,value in self.settings_map.items():
            settings_tab_layout += [[sg.Text(text=value['label'])],
                                    [sg.Input(key=value['ui_key'])]]
        settings_tab_layout += [[sg.Button(button_text='Restore defaults',
                                           key=self.key_reset_settings_button)]]    


        layout = [[sg.TabGroup([[sg.Tab('Main', main_tab_layout),
                                 sg.Tab('Settings',settings_tab_layout),
                                 sg.Tab('Consoles',console_tab_group)]],
                               enable_events=True, key=self.key_top_tabgroup)],
                  [sg.Button('Start', key=self.key_run_button),
                   sg.Button('Stop', key=self.key_kill_button)]]            

        self.window = sg.Window('JackTrip Control', layout, finalize=True)
        

        self.reset_settings()
        self.update_console_commands()
        self.reset()
    
    def reset_settings(self):
        """ populate UI with values from config"""
        print(self.settings_map)
        for key, value in self.settings_map.items():
            print(value)
            self.window[value['ui_key']].update(value=value['value'])
        
    
    def update_console_commands(self):
        # cfg = self.moduleConfig # for clearer code
        # jack_root = cfg['jack_root'].as_filename()
        # jacktrip_root = cfg['jacktrip_root'].as_filename()
        # sample_rate = cfg['sample_rate'].get(int)
        # buffer_size = cfg['buffer_size'].get(int)
        # asio_soundcard_name = cfg['asio_soundcard_name'].get(str)
        cfg=dict()
        for key, value in self.settings_map.items():
            cfg[key] = self.window[value['ui_key']].get()
            print(f'{key}: {cfg[key]}')
            # self.window[value['ui_key']].update(value=value['func']())
        
        # commands
        cmd_wsl_jack = f'wsl -u root jackd -d dummy -r {cfg["sample_rate"]} -p {cfg["buffer_size"]}'
        cmd_wsl_jacktrip = 'wsl -u root jacktrip -s --nojackportsconnect'
        cmd_local_jack = (f'{cfg["jack_root"]}/jackd.exe -S ' +
                          f'-dportaudio -d\"{cfg["asio_soundcard_name"]}\" ' + 
                          f'-r{cfg["sample_rate"]} -p{cfg["buffer_size"]}')
        cmd_local_jacktrip = (f'{cfg["jacktrip_root"]}/jacktrip.exe -c {self.ip} ' +
                              f'--clientname {self.ip} --nojackportsconnect')
        # breaking encapsulation principle here!
        self.window[self.pr_wsl_jack.key_cmd].update(value=cmd_wsl_jack)
        self.window[self.pr_wsl_jt.key_cmd].update(value=cmd_wsl_jacktrip)
        self.window[self.pr_local_jack.key_cmd].update(value=cmd_local_jack)
        self.window[self.pr_local_jt.key_cmd].update(value=cmd_local_jacktrip)

        
        
        # these commands haven't got a ui element to store them in
        self.local_jackconnect_exe = f'{cfg["jack_root"]}/jack_connect.exe'
        self.kill_wsl_jack = 'wsl -u root pkill -f jackd'
        # self.kill_local_jack = 
        
        
    
    
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
            elif event == self.key_top_tabgroup:
                # tab changed so make sure values are up to date
                self.update_console_commands()
            elif event == self.key_reset_settings_button:
                self.reset_settings()
            elif event == self.key_run_button:
                # stop before we start
                if self.waiting or self.running:
                    for tab in self.console_tabs:
                        if tab.is_running():
                            tab.stop()
                    self.reset()        
                
                for tab in self.console_tabs:
                    tab.start(self.window)
                self.stopped = False
                self.waiting = True
                
            elif event == self.key_kill_button:
                for tab in self.console_tabs:
                    tab.stop()
                self.reset()
                
            # update display on every loop
            for tab in self.console_tabs:
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
            cmd = f'{self.local_jackconnect_exe} {self.ip}:receive_{channel} system:playback_{channel}'
            completed_process = subprocess.run(cmd, text=True, capture_output=True)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--asio_soundcard_name', help='device name used by jack to identify the soundcard')
    args = parser.parse_args()
    thegui = Gui(args)
    thegui.monitor()
    

    