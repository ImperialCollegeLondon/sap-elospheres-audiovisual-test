import probestrategy
import avrenderercontrol

# import gui

import PySimpleGUI as sg
import importlib
import time
import random
import numpy as np


# def getLayout():
#     """Defines the overall layout of the GUI and keys for the elements"""
#     layout = [[sg.Text('Probe level:'), sg.Text(size=(15,1), key=psKey)],
#               [sg.Input(key='-IN-')],
#               [sg.Button('Next'), sg.Button('Exit')]]

def scoreResponse(response):
    """Temporary function in liu of an extensible approach"""
    # convert a string representing int between 0 and 5 to a fraction
    return float(response)/5


def isValidResponse(response):
    try:
        response = float(response)
    except:
        print('Not a number')
        return False

    if (response < 0) or (response > 5):
        print('Out of range')
        return False

    if (np.remainder(response, 1) != 0):
        print('Not an integer')
        return False

    return True


def instance_builder(config):
    """ Returns a class instance given a dict with keys
        class: fully qualified class name
        settings: dict of parameters which the class constructor takes
    """
    module_name, class_name = config["class"].rsplit(".", 1)
    callable_class_constructor = getattr(importlib.import_module(module_name),
                                         class_name)
    return callable_class_constructor(config["settings"])


def run_block(config):
    """Main function for executing a test
    TODO:
    The number of trials is limited by the lowest of
    - config: can directly impose a maximum
    - probe_strategy: convergence achieved or fixed number of trials specified
    - materials: if pre generated materials are used (avrenderer or
                 responsemode?)

    """

    # settings
    pre_trial_delay = (0.1, 0.2)

    # AVRendererControl
    with instance_builder(config["AVRendererControl"]) as avrenderer:

        # ProbeStrategy
        probe_strategy = instance_builder(config["ProbeStrategy"])

        # TODO: ensure probe strategy is compatable with the avrenderer

        # ResponseMode
        response_mode = instance_builder(config["ResponseMode"])

        # start test
        #    - play background video
        #    - play background audio
        avrenderer.start_scene()

        # wait for experimenter
        input('Scene has started. Press Enter to start first trial...')

        # main loop
        while not probe_strategy.is_finished():

            # Get required parameters
            stimulus_id = probe_strategy.get_next_stimulus_id()
            probe_level = probe_strategy.get_next_probe_level()

            # console feedback
            print('Presenting trial...')
            print('stimulus_id: ' + str(stimulus_id))
            print('probe_level:' + probe_strategy.get_next_probe_level_as_string())

            # Prepare the renderer (behaviour depends on  implementation)
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
            avrenderer.present_trial(stimulus_id)

            # Wait for response
            # - result type depends on the response mode
            # - ProbeStrategy and ResponseMode must be chosen to be compatible
            result = response_mode.wait()

            if result is None:
                # window was closed/cancelled - attempt to end gracefully
                break

            probe_strategy.store_trial_result(result)

        print(str(probe_strategy.get_current_estimate()))
        return


if __name__ == '__main__':
    #  TODO: Implement passing config from command line

    run_block(block_config)
