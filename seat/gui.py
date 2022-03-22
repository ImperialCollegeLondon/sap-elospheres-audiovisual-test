import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import pathlib
import PySimpleGUI as sg
import sys
import traceback
import yaml

import jacktripcontrol
import seat
import util



class ExperimentBlockSelector():
    """
    A window is created allowing the experimentor to select which block
    to run.
    """
    def __init__(self, csv_file, jtc=None):
        # read the csv file
        df = pd.read_csv(csv_file)
        print(df)
    
        subject_id_list = df.subject_id.unique().tolist()
        print(subject_id_list)
    
        # define the gui
        label_size = (14,1)
        key_meta_name = "subject_name"
        key_meta_age = "subject_age"
        key_meta_sex = "subject_sex"
        meta_keys = [key_meta_name, key_meta_age, key_meta_sex]
        key_subject_combo = "-subject-"
        key_block_listbox = "-block-"
        key_config_text = "-config-"
        key_run_button = "-run-"
        key_jtc_button = "-jtc-"
    
        # conditions as a separate thing for readability
        condition_keys = df.columns
        condition_display_layout = [[sg.Text(key, size=label_size, justification='right')] +
                                    [sg.Input('', key=key, size=(60,1),
                                              justification='left', disabled=True,
                                              text_color='grey')]
                                    for key in condition_keys]
    
    
        layout = [[sg.Text('Enter participant details (optional, unvalidated)')],
                  [sg.Text('Name',size=label_size, justification='right'),
                   sg.Input(key=key_meta_name)],
                  [sg.Text('Age',size=label_size, justification='right'),
                   sg.Input(key=key_meta_age)],              
                  [sg.Text('Sex',size=label_size, justification='right'),
                   sg.Input(key=key_meta_sex)],
                  [sg.Text('Select the subject then the block number')],
                  [sg.Text('Subject: ',size=label_size, justification='right'),
                   sg.Combo(subject_id_list, key=key_subject_combo, enable_events=True, size=(8,1))],
                  [sg.Text('Block: ',size=label_size, justification='right'),
                   sg.Listbox([''], key=key_block_listbox, enable_events=True, size=(8,10), disabled=True)],
                  [sg.Text('Config: ',size=label_size, justification='right'),
                   sg.Input('', key=key_config_text, size=(60,1), justification='right',disabled=True,text_color='grey')],
                  [sg.HorizontalSeparator()]
                  ]
        layout += [[sg.Text('Condition specification for selected block')]]
        layout += condition_display_layout
        layout += [sg.HorizontalSeparator()],
        layout += [[sg.Button('JTC...', key=key_jtc_button, disabled=True)],
                   [sg.Button('Run', key=key_run_button, focus=True,
                                  disabled=True)]]

        window = sg.Window('SEAT block selector', layout,
                                    keep_on_top=False,
                                    return_keyboard_events=True,
                                    # use_default_focus=False,
                                    finalize=True)
        if jtc is not None:   
            window[key_jtc_button].update(disabled=False)                        
            jtc.start(raise_error=True,
                      connect_mode=jacktripcontrol.ConnectMode.NON_BLOCKING)
            jtc_colors = {jacktripcontrol.State.DISCONNECTED: 'red',
                          jacktripcontrol.State.STARTING: 'orange',
                          jacktripcontrol.State.CONNECTED: 'green'}

        while True:             # Event Loop
            event, values = window.Read(timeout=50)
            # print(event, values)
        
        
            if event == sg.WIN_CLOSED:
                window.close()
                return
            elif event == key_subject_combo:
                subject_id = values[key_subject_combo]
                # subject_id = values
                # print(f'Selected subject {subject_id}')
                # populate block combo
                block_id_list = df[df.subject_id==subject_id].block_id.unique().tolist()
                window[key_block_listbox].update(values=block_id_list)
                # window[key_block_listbox].update(value='', disabled=False)
                window[key_block_listbox].update(set_to_index=0, disabled=False)
                window[key_config_text].update(value='')
                window[key_run_button].update(disabled=True)
                for key in condition_keys:
                        window[key].update(value='')
                window.refresh()
            elif event == key_block_listbox:
                block_id = values[key_block_listbox][0]
                print(f'Selected block {block_id}')
                block_indexes = window[key_block_listbox].get_indexes()
                print(f'Selected block indexes {block_indexes}')
                subject_id = values[key_subject_combo]
                # find a matching directory
                search_str = f'{subject_id}_{block_id}_*/config.yml'
                print(search_str)
                matches = sorted(pathlib.Path(csv_file).parent.glob(search_str))
            
                # find a matching row
                idx = np.flatnonzero((df.subject_id==subject_id) & (df.block_id==block_id))
            
                if (len(matches) != 1) or (len(idx) != 1):
                    # can't uniquely determine the condition
                    window[key_config_text].update(value='')
                    window[key_run_button].update(disabled=True)
                    for key in condition_keys:
                        window[key].update(value='')
                else:
                    window[key_config_text].update(value=str(matches[0]))
                    window[key_run_button].update(disabled=False)
                    for key in condition_keys:
                        window[key].update(value=df[key].iloc[idx].item())
                
            elif event == key_jtc_button:
                # this can only happen if button is enabled
                gui = jacktripcontrol.Gui(jtc)
                gui.show()            
            elif event == key_run_button:
                subject_id = values[key_subject_combo]
                block_id = values[key_block_listbox][0]
            
                # prepare metadata as single row dataframe
                subject_data = dict([(key, window[key].get()) for key in meta_keys])
                # n.b. need to wrap dict in list
                subject_data = pd.DataFrame.from_records([subject_data])

                condition_data = df.loc[(df.subject_id==subject_id) & (df.block_id==block_id)]
            
            
                config_file = pathlib.Path(window[key_config_text].get())
                # print(config_file)
                datestr = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_dir = pathlib.Path(config_file.parent, datestr)
            
                # by now we should have a value for out_dir
                try:
                    out_dir.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    print(f'Output directory {out_dir} already exists.')
                    break
            
                with open(config_file, 'r') as f:
                    block_config = yaml.safe_load(f)
                    if ("App" in block_config):
                        raise NotImplementedError("Deal with App.log_dir")
                    else:
                        block_config["App"] = {"log_dir": str(out_dir)}
                    
                    # try:
                    seat.run_block(block_config, subject_data=subject_data,
                                   condition_data = condition_data)
                    block_success = True               
                    # except Exception as e:
    #                     tb = traceback.format_exc()
    #                     # tb = e.format_exc()
    #                     block_success = False
    #                     print(f'An error happened.  Here is the info:', e)
    #                     sg.popup_error(f'Something went wrong running the test!\nCheck the console for more information.\n\nThe block index will NOT be incremented.', e)
            
                # tidy up
                # - get the current blocl
                if block_success:
                    print(f'Finished block_id {block_id}')
                    # Sanity check that the selected index still corresponds to the retained value
                    # new_block_id = values[key_block_listbox][0]
    #                 print(f'Selected block is now {block_id}')
    #                 print(f'Selected block indexes {block_indexes}')
                    block_indexes = window[key_block_listbox].get_indexes()                
                    current_index = block_indexes[0]
                    list_values = window[key_block_listbox].get_list_values()
                    print(f'len(list_values): {len(list_values)}')
                    if list_values[current_index] != block_id:
                        # Something's gone wrong with the values - so don't try to be clever
                        pass
                    else:
                        current_index += 1
                        if current_index >= (len(list_values)):
                            # finished last block
                            print(f'That was the last block')
                            window[key_block_listbox].set_value([])
                            # window[key_block_listbox].update(set_to_index=0, disabled=False)
                            window[key_config_text].update(value='')
                            window[key_run_button].update(disabled=True)
                            for key in condition_keys:
                                    window[key].update(value='')
                            window.refresh()
                        else:
                            window[key_block_listbox].update(set_to_index=current_index)
                            window.refresh()
                            block_id = window[key_block_listbox].get()[0]
                            print(f'Selecting next block... block_id: {block_id}')
                
                
                

            # update gui
            if jtc is not None:
                window[key_jtc_button].update(button_color=('black',jtc_colors[jtc.state]))
                        



if __name__ == '__main__':
    # parse the command line inputs
    parser = jacktripcontrol.JTCArgumentParser()
    parser.add_argument("-f", "--file",
                        help="conditions file (.csv)")
    parser.add_argument("--disable-jtc", action='store_true', help="Do not do JactTripControl")
    # parser.add_argument("-o", "--out-dir",
    #                     help="output directory for logs/results")
    args = parser.parse_args()
    print(args)
    
    # file
    # - use the provided option otherwise pop a dialoge to choose it
    if args.file is not None:
        file = args.file
        print('Config file: ' + file)
    else:
        # get file
        file = sg.popup_get_file(
            'Choose the condition specification file',
            file_types=(('csv', '*.csv'),)
            )
    if file is None:
        sys.exit()
    else:
        file = pathlib.Path(file)
        try:
            util.check_path_is_file(file)
        except FileNotFoundError:
            print('No csv file found at ' + str(file))
            sys.exit()
    
    disable_jtc = args.disable_jtc
    
    # remain args are for jacktripcontrol
    del args.file   
    del args.disable_jtc
    if disable_jtc:
        ebs = ExperimentBlockSelector(file)
    else:   
        jtc = jacktripcontrol.JackTripControl(args)    
        jtc.kill()
        ebs = ExperimentBlockSelector(file, jtc) #blocks
        jtc.stop()