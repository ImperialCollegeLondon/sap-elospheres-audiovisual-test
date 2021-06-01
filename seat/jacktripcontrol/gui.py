import confuse
import os
import PySimpleGUI as sg
import yaml

import jacktripcontrol

class TabbedProcessView:
    """
    Helper class to wrap up some of the UI elements
    """
    def __init__(self, key=None):
        self.key = key   

        if self.key is None:
            raise ValueError('key must be set')

        self.maximum_history = 30 # number of lines in the console
        self.element_width = 60

        self.key_cmd = f'{key}.--command--'
        self.key_console = f'{key}.--console--'


    def create_layout(self):
        self.layout = [[sg.Text('Command:')],
                       [sg.Input(key=self.key_cmd, size=(self.element_width, 1),
                                 default_text='',
                                 readonly=True,
                                 text_color='black',
                                 disabled_readonly_text_color='grey')],
                       [sg.Text('Console log:')],
                       [sg.Text('', key=self.key_console,
                                size=(self.element_width, self.maximum_history),
                                text_color='white', background_color='black')]
                      ]
        return self.layout
    
    def set_command(self, window, cmd_str):
        window[self.key_cmd].update(value=cmd_str)
        
    def update_console(self, window, log):
        window[self.key_console].update(value=log)

                                        
class Gui:
    """
    A user interface wrapper for JackTripControl (jtc)
    Allows the jtc instance to be started/stopped, the consoles for each 
    process to be viewed and the settings to be changed, saved and restored.
    """
    def __init__(self, jtc):
        # expect the supplied jtc to already to use
        self.jtc = jtc
         
        # keys to ui elements
        self.key_timeout = '--timeout--'
        self.key_top_tabgroup = '--tabgroup--'
        self.key_restore_settings_button = '--restore-settings--'
        self.key_save_settings_button = '--save-settings--'
        self.key_run_button = '--run--'
        self.key_stop_button = '--stop--'
        self.key_status_text = '--status--'
        self.key_kill_button = '--kill--'
        
        # create objects to display process consoles
        # name them so that we can control the order
        self.console_tab_keys = ['wsl_jack','wsl_jacktrip',
                                 'local_jack','local_jacktrip']
        self.console_tabs = [TabbedProcessView(key=key) 
                             for key in self.console_tab_keys]
        # for key,val in self.jtc.lp_all.items():
        #     self.console_tabs.append(TabbedProcessView(key=key))

        # intialise locally stored values used to avoid writing to the gui more
        # than necessary - make empty to ensure they get updated the first time
        self.prev_state = []
        self.prev_log = {}
        for tab in self.console_tabs:
            self.prev_log[tab.key] = []

    
    def map_cfg_to_settings(self):
        """
        Single place to define the keys, labels and helper functions associated
        with the settings

        Returns
        -------
        map_dict : dict
            Each key in the dict is a setting
            Each value is itself a dict with the following entries:
                label: string used to describe the setting in the UI
                cfg2str: the value of the setting stored as a string
                func_str2cfg: function used to convert the value from a string
                             (as returned by the UI) into the proper type

        """
        cfg = self.jtc.moduleConfig
        map_dict = {'jack_root': {'label': 'Root directory for Jack',
                                  'cfg2str': cfg['jack_root'].as_filename(),
                                  'func_str2cfg': str},
                    'jacktrip_root': {'label': 'Root directory for JackTrip',
                                      'cfg2str': cfg['jacktrip_root'].as_filename(),
                                      'func_str2cfg': str},
                    'sample_rate': {'label': 'Sample rate [Hz]',
                                    'cfg2str': str(cfg['sample_rate'].get(int)),
                                    'func_str2cfg': int},
                    'buffer_size': {'label': 'Buffer size [samples]',
                                    'cfg2str': str(cfg['buffer_size'].get(int)),
                                    'func_str2cfg': int},
                    'asio_soundcard_name': {'label': 'ASIO sound card name (as reported by portaudio)',
                                            'cfg2str': cfg['asio_soundcard_name'].get(str),
                                            'func_str2cfg': str}
                   }
        # print(map_dict)
        return map_dict
    
    
    def ui_settings_to_dict(self):
        """
        Gets the settings values and returns as a dict. Makes use of the 
        'func_str2cfg' function returned by map_cfg_to_settings()

        Returns
        -------
        args : dict
            Settings as a dict.

        """
        args = dict()
        for key, value in self.map_cfg_to_settings().items():
            # print(key)
            # self.jtc.moduleConfig[key] = value['func_str2cfg'](self.window[key].get())
            args[key] = value['func_str2cfg'](self.window[key].get())
        return args
    
    def update_settings_from_ui(self):
        """
        updates jtc.moduleConfig according to the values in the UI

        """
        args = self.ui_settings_to_dict()
        # print('get_settings_from_ui:')
        # print(args)
        self.jtc.moduleConfig.set_args(args)
        # print(self.jtc.moduleConfig)

    def populate_settings(self):
        """
        updates the UI according to the values in jtc.moduleConfig

        """
        for key, value in self.map_cfg_to_settings().items():
            # print(value)
            self.window[key].update(value=value['cfg2str'])

    def restore_settings(self):
        """ 
        updates with the settings from the package defaults
        """
        # print('\n\n\nrestore_settings\n\n\n')
        # print(self.jtc.moduleConfig)
        app_name = 'JackTripControl'
        self.jtc.moduleConfig = confuse.Configuration(app_name, __name__,
                                                      read=False)
        self.jtc.moduleConfig.read(user=False, defaults=True)
        # print(self.jtc.moduleConfig)
        self.populate_settings()
            
    def save_settings(self):
        """
        saves the current settings to user's own configuration
        """
        # original method - based on confuse documentation
        # resulting file is very complicated - multiple overlays
        # self.update_settings_from_ui()
        # config_filename = os.path.join(self.jtc.moduleConfig.config_dir(),
        #                        confuse.CONFIG_FILENAME)
        # print(f'Saving to {config_filename}')
        # with open(config_filename, 'w') as f:
        #     yaml.dump(self.jtc.moduleConfig, f)
        cfg_dict = self.ui_settings_to_dict()
        config_filename = os.path.join(self.jtc.moduleConfig.config_dir(),
                               confuse.CONFIG_FILENAME)
        # print(f'Saving to {config_filename}')
        with open(config_filename, 'w') as f:
            yaml.dump(cfg_dict, f)    
            
        
    def update_process_command_strings(self):
        if self.jtc.state is jacktripcontrol.State.DISCONNECTED:
            self.update_settings_from_ui()
            self.set_console_commands()
    
    
    def set_console_commands(self):
        cmd_dict = self.jtc.get_commands()
        for tab in self.console_tabs:
            tab.set_command(self.window, cmd_dict[tab.key]['start'])

    def update_console_logs(self):
        if self.jtc.lp is not None:
            # print(self.jtc.lp)
            for tab in self.console_tabs:
            
                # if self.jtc.lp_all[tab.key].log is not self.prev_log[tab.key]:
                # print(tab.key)
                
                tmp_log = self.jtc.lp[tab.key].get_log()
                tab.update_console(self.window, tmp_log)
                self.prev_log[tab.key] = tmp_log
           
    def update_state(self):
        if self.jtc.state is not self.prev_state:
            self.window[self.key_status_text].update(value=str(self.jtc.state))
            self.prev_state = self.jtc.state
        
    def show(self):
        """
        Displays the GUI so that users can interact with it

        """
        # must always create the layout from new
        console_tab_group = [[sg.TabGroup([[sg.Tab(tab.key, tab.create_layout()) for tab in self.console_tabs]])]]
        main_tab_layout = [[sg.Text(text='This is the main tab. We will write something here soon')]]

        settings_tab_layout = [[]]
        for key,value in self.map_cfg_to_settings().items():
            # print(f'{key}: {value}')
            settings_tab_layout += [[sg.Text(text=value['label'])],
                                    [sg.Input(key=key)]]
        settings_tab_layout += [[sg.Button(button_text='Restore defaults',
                                           key=self.key_restore_settings_button),
                                 sg.Button(button_text='Save',
                                           key=self.key_save_settings_button)]]    


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
        self.populate_settings()
        self.set_console_commands()
        

        # counter = 0
        while True:             # Event Loop
            # counter+=1
            # print(f'Event loop {counter}')
            
            event, values = self.window.Read(timeout=50,timeout_key=self.key_timeout)
            if event is not self.key_timeout:
                # print(event, values)
                pass
            
            if event == sg.WIN_CLOSED:
                self.window.close()
                return
            
            elif event == self.key_top_tabgroup:
                # tab changed so make sure values are up to date
                self.update_process_command_strings()
                
            elif event == self.key_restore_settings_button:
                self.restore_settings()
            
            elif event == self.key_save_settings_button:
                self.save_settings()
                
            elif event == self.key_run_button:
                # start but don't block so UI can update
                self.jtc.start(connect_mode=jacktripcontrol.ConnectMode.NON_BLOCKING)
                # self.jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING)
                # self.jtc.start(connect_mode=jacktripcontrol.ConnectMode.NO_CONNECT)
            elif event == self.key_stop_button:
                self.jtc.stop()

            elif event == self.key_kill_button:
                self.jtc.kill()
                
            # update display on every loop
            self.update_state() # show the current state of jtc in the gui
            self.update_console_logs()
            #TODO enable/disable buttons according to state
