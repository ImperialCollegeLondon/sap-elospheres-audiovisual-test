import argparse
import confuse
from datetime import datetime
import enum
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
        self.key_stop_button = '--stop--'
        self.key_status_text = '--status--'
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
        
        self.state = State.DISCONNECTED
    
    def reset_settings(self):
        """ populate UI with values from config"""
        # print(self.settings_map)
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
        self.cmd_kill_wsl_jack = 'wsl -u root pkill -f jackd'
        self.cmd_kill_local_jack = 'taskkill /F /IM jackd.exe /IM jacktrip.exe'

        
    def set_state(self, state):
        self.state = state
        self.window[self.key_status_text].update(value=str(self.state))

        
    def show(self):
        # must always create the layout from new
        console_tab_group = [[sg.TabGroup([[sg.Tab(tab.key, tab.create_layout()) for tab in self.console_tabs]])]]
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
                   sg.Button('Stop', key=self.key_stop_button),
                   sg.Text(key=self.key_status_text,size=(15,1),justification='center'),
                   sg.Button('Kill', key=self.key_kill_button)]]            

        # everything has been created ready to go
        self.window = sg.Window('JackTrip Control', layout, finalize=True)
        self.reset_settings() #TODO store settings and use restore settings
        self.update_console_commands()
        self.set_state(self.state) # force UI update

        
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
                if self.state in [State.CONNECTED, State.STARTING]:
                    for tab in self.console_tabs:
                        if tab.is_running():
                            tab.stop()
                    self.set_state(State.DISCONNECTED)        
                
                for tab in self.console_tabs:
                    tab.start(self.window)
                self.set_state(State.STARTING) 
                
            elif event == self.key_stop_button:
                for tab in self.console_tabs:
                    tab.stop()
                self.set_state(State.DISCONNECTED)
            elif event == self.key_kill_button:
                # be brutal
                completed_process = subprocess.run(self.cmd_kill_wsl_jack, text=True, capture_output=True)
                completed_process = subprocess.run(self.cmd_kill_local_jack, text=True, capture_output=True)
                
            # update display on every loop
            for tab in self.console_tabs:
                tab.update(self.window)

            # update status
            if self.state is State.STARTING:
                if (self.pr_local_jt.output_contains(self.window, self.ready_string) and
                    self.pr_wsl_jt.output_contains(self.window, self.ready_string)):

                    # connect jacktrip to soundcard
                    self.connect_jacktrip_to_output()
                    self.set_state(State.CONNECTED)

                
Error gui has to change in sync with new jacktripcontrol
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--asio_soundcard_name', help='device name used by jack to identify the soundcard')
    args = parser.parse_args()
    thegui = Gui(args)
    thegui.show()
    

    