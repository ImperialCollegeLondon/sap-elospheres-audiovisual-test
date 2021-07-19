import avrenderercontrol
import probestrategy
import seatlog as sl
import util

import argparse
from datetime import datetime
import importlib
import numpy as np
import pathlib
import pandas as pd
import pylsl
import PySimpleGUI as sg
import random
import socket
import sys
import time
import yaml




def instance_builder(config):
    """ Returns a class instance given a dict with keys
        class: fully qualified class name
        settings: dict of parameters which the class constructor takes
    """
    module_name, class_name = config["class"].rsplit(".", 1)
    callable_class_constructor = getattr(importlib.import_module(module_name),
                                         class_name)
    return callable_class_constructor(config["settings"])


def run_block(config, block_id=0, subject_data=None, condition_data=None):
    """Main function for executing a test
    TODO:
    The number of trials is limited by the lowest of
    - config: can directly impose a maximum
    - probe_strategy: convergence achieved or fixed number of trials specified
    - materials: if pre generated materials are used (avrenderer or
                 responsemode?)

    """
    do_send_lsl = True
    do_debug_lsl = True
    do_labrecorder_remote_control = True
    labrecorder_ip_port = ("localhost", 22345) # default
    
    log_dir = config["App"]["log_dir"]
    

    if (subject_data is None):
        # minimal empty data
        subject_data = pd.DataFrame([['']], columns=['subject_id'])
    else:
        # basic checks
        if not isinstance(subject_data, pd.DataFrame):
            raise TypeError('subject_data should be a DataFrame')
        if (subject_data.shape[0] != 1):
            raise ValueError('subject_data should have a single row')

    if (condition_data is None):
        # minimal empty data
        condition_data = pd.DataFrame([['']], columns=['condition_id'])
    else:
        # basic checks
        if not isinstance(condition_data, pd.DataFrame):
            raise TypeError('condition_data should be a DataFrame')
        if (subject_data.shape[0] != 1):
            raise ValueError('condition_data should have a single row')
    
    # Define the stream properties + open outlet
    # uid = subject_data.subject_id[0] + condition_data.
    if do_send_lsl:
        info = pylsl.StreamInfo(name='SeatApp',
                                type='markers',
                                channel_count=1,
                                nominal_srate=pylsl.IRREGULAR_RATE,
                                channel_format=pylsl.cf_string,
                                source_id='seat-markers-123')
        outlet = pylsl.StreamOutlet(info)
    
    # control LabRecorder
    if do_labrecorder_remote_control:
        try:
            lsl_recorder_rc = socket.create_connection(labrecorder_ip_port)
        except Exception as err:
            print('\n\nThere was a problem establishing remote control over LabRecorder:\n' +
                  f'IP: {labrecorder_ip_port[0]}\n' +
                  f'port: {labrecorder_ip_port[1]}\n' + 
                  'error message follows...\n\n')
            raise err

        # wait a bit to establish the connection
        time.sleep(1)
        
        # set the xdf file path
        if do_debug_lsl:
            # use a hardcoded directory and timestamp for xdf path
            template_str =  f"{pathlib.PurePath(log_dir).name}.xdf"
            debug_dir = str(pathlib.PurePath('C:\\Users\\alastair\\Dropbox\\ELOSPHERES\\data\\20210630_lsl_development'))
            lsl_recorder_rc.sendall(("filename " +
                                     f"{{root:{debug_dir}}} " +           # string
                                     f"{{template:{template_str}}} " +  # string
                                     "\n").encode())
        else:
            # xdf path should correspond to the logs
            # TODO: pass in parameters
            template_str = 'subject_%p_block_%n_condition_%b.xdf'
            subj_str = str(subject_data)
            cond_str = str(condition_data)
            
            lsl_recorder_rc.sendall(("filename " +
                                      f"{{root:{log_dir}}} " +           # string
                                      f"{{template:{template_str}}} " +  # string
                                      f"{{participant:{subj_str}}}" +    # string
                                      f"{{task:{cond_str}}}" +           # string
                                      f"{{run:{block_id}}}" +            # int
                                      "\n").encode())
    
        time.sleep(4)
        # lsl_recorder_rc.sendall(b"start\n")
        # time.sleep(2)
    
    # settings
    pre_trial_delay = (0.1, 0.2)

    log_path = pathlib.Path(log_dir, 'log.csv')
    with sl.CSVLogger(log_path) as mylogger:
    
    
        # AVRendererControl
        with instance_builder(config["AVRendererControl"]) as avrenderer:
    
            # ProbeStrategy
            config["ProbeStrategy"]["settings"]["log_path"] = pathlib.Path(
                config["App"]["log_dir"], 'probe_log.csv')
            probe_strategy = instance_builder(config["ProbeStrategy"])
    
            # ResponseMode
            config["ResponseMode"]["settings"]["log_path"] = pathlib.Path(
                config["App"]["log_dir"], 'response_log.csv')
            response_mode = instance_builder(config["ResponseMode"])
    
            # TODO: ensure compatibility of probe_strategy, response_mode and
            #       avrenderer
    
            # start test
            #    - play background video
            #    - play background audio
            if do_send_lsl:
                outlet.push_sample(['{"event_id":"start_scene"}'])
            avrenderer.start_scene()
            time.sleep(4)
            
            
            # force update of labrecorder to make sure we have tascar's lsl stream
            if do_labrecorder_remote_control:
                lsl_recorder_rc.sendall(b"update\n")
            
            # wait for experimenter
            if do_labrecorder_remote_control:
                lr_prompt_str = 'Check LabRecorder can see all the streams and has started recording.\n'
            else:
                lr_prompt_str = ''
            response_mode.continue_when_ready(
                f'Scene has started.\n{lr_prompt_str}Press Enter to start first trial...')
    
    
            # main loop
            trial_id = 0  # 1-based counter is incremented at start of loop
            while not probe_strategy.is_finished():
    
                trial_id += 1
                
                # Get required parameters
                stimulus_id = probe_strategy.get_next_stimulus_id()
                probe_level = probe_strategy.get_next_probe_level()
    
                # console feedback
                print('Presenting trial...')
                print('stimulus_id: ' + str(stimulus_id))
                print('probe_level:'
                      + probe_strategy.get_next_probe_level_as_string())
    
                # Prepare the renderer (behaviour depends on  implementation)
                if do_send_lsl:
                    outlet.push_sample([(f'{{"trial": {trial_id}, ' +
                                         '"event_id": "set_probe_level", ' +
                                         f'"probe_level": {str(probe_level)} }}')])
                avrenderer.set_probe_level(probe_level)
    
                # Show the response display UI
                response_mode.show_prompt(stimulus_id)
    
                # Pause
                # (random duration between preTrialDelay[0] and preTrialDelay[1])
                time.sleep(pre_trial_delay[0]
                           + ((pre_trial_delay[1]-pre_trial_delay[0])
                              * random.random()))
    
                # Present the stimulus//mixture
                # e.g. send OSC commands to start videos/samplers
                if do_send_lsl:
                    outlet.push_sample([(f'{{"trial": {trial_id}, ' +
                                         '"event_id": "present_trial", ' +
                                         f'"stimulus_id": {str(stimulus_id)} }}')])
                avrenderer.present_trial(stimulus_id)
    
                # Wait for response
                # - result type depends on the response mode
                # - ProbeStrategy and ResponseMode must be chosen to be compatible
                result = response_mode.wait()
    
                if result is None:
                    # window was closed/cancelled - attempt to end gracefully
                    break
    
                probe_strategy.store_trial_result(result)
    
                # Trial is finished. Collect and push log data
                mylogger.append(trial_id, subject_data)
                mylogger.append(trial_id, condition_data)
                mylogger.append(trial_id, probe_strategy.get_trial_data(), 
                                prefix='ps_')
                mylogger.append(trial_id, avrenderer.get_trial_data(),
                                prefix='av_')
                mylogger.append(trial_id, response_mode.get_trial_data(),
                                prefix='rm_')
            
            print(str(probe_strategy.get_current_estimate()))
            
            if do_send_lsl:
                outlet.push_sample(['{"event_id":"done"}'])
                time.sleep(1)
            
            if do_labrecorder_remote_control:
                lsl_recorder_rc.sendall(b"stop\n")
                time.sleep(1)
            
            return


if __name__ == '__main__':
    # parse the command line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="config file (.yml)")
    parser.add_argument("-o", "--out-dir",
                        help="output directory for logs/results")
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
            'Choose the config file',
            file_types=(('yml', '*.yml'),)
            )
    if file is None:
        sys.exit()
    else:
        file = pathlib.Path(file)
        try:
            util.check_path_is_file(file)
        except FileNotFoundError:
            print('No config file found at ' + str(file))
            sys.exit()

    # read in the config values
    with open(file, 'r') as f:
        block_config = yaml.safe_load(f)

    # got the configuration, now need to arbitrate between values provided in
    # file and those on the command line
    # - precedence should be
    #     1: command line
    #     2: config file
    #     3: fail-safe default for any essential entries

    # out-dir
    # - fail-safe is a datestamped directory relative to the config file
    out_dir = args.out_dir
    if out_dir is not None:
        out_dir = pathlib.Path(out_dir)
        print('Output directory from command line: ' + str(out_dir))

    if out_dir is None:
        if ("App" in block_config) and ("log_dir" in block_config["App"]):
            out_dir = pathlib.Path(block_config["App"]["log_dir"])
            print('Output directory from config file: ' + str(out_dir))

    if out_dir is None:
        datestr = datetime.now().strftime("%Y%m%d_%H%M%S")
        if (file.name in ('config.yml')):
            # This is default and pretty meaningless
            # so a sibling directory should be ok
            # TODO: Add check for multiple yml files in directory
            out_dir = pathlib.Path(file.parent, datestr)
        else:
            # make a subdirectory with the same name as the config file
            config_file_as_dir = file.with_suffix('')
            out_dir = pathlib.Path(config_file_as_dir, datestr)
        print('Output directory (auto-generated): ' + str(out_dir))

    # by now we should have a value for out_dir
    try:
        out_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print('The output directory already exists.')
        sys.exit()

    # write/overwrite the entry back into config
    if ("App" in block_config):
        block_config["App"]["log_dir"] = str(out_dir)
    else:
        block_config["App"] = {"log_dir": str(out_dir)}

    # finally, run the block
    run_block(block_config)
