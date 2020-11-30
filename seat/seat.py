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

        # TODO: validate that the probe strategy is compatable with the avrenderer

        # setup the gui
        ps_key = '-ProbeDetails-'
        materials_key = '-Materials-'
        response_key = '-Response-'
        layout = [[sg.Text('Probe level:'), sg.Text(size=(15, 1), key=ps_key)],
                  [sg.Text('Keywords:'), sg.Text(size=(80, 1), key=materials_key)],
                  [sg.Input(key=response_key, focus=True)],
                  [sg.Button('Next')]]

        window = sg.Window('SAP ELO-SPHERES AV Test', layout,
                           finalize=True, use_default_focus=False)

        # start test
        #    - play background video
        #    - play background audio
        avrenderer.start_scene()

        # wait for experimenter
        while True:
            window[response_key].update(
                'Press Next when ready to proceed with test')
            event, values = window.read()
            print(event, values)
            if event == sg.WIN_CLOSED:
                window.close()
                return
            if event == 'Next':
                break

        # main loop
        while not probe_strategy.is_finished():

            # doTrial
            # - getProbeLevel
            probe_level = probe_strategy.get_next_probe_level()

            thisTrialMaterial = random.sample(
                ['Boy', 'Girl', 'Dog', 'Cat', 'Plane', 'Car', 'Sun', 'Moon'], k=5)

            # - showExperimenterUI
            window[ps_key].update(str(probe_level))
            window[materials_key].update(str(thisTrialMaterial))
            window[response_key].update('')

            # - prepareTrial
            #     e.g. send OSC commands to set levels of source(s)
            avrenderer.set_probe_level(probe_level)

            # - pause
            # (random duration between preTrialDelay[0] and preTrialDelay[1])
            time.sleep(pre_trial_delay[0]
                       + (pre_trial_delay[1]-pre_trial_delay[0]) * random.random())

            # - [present stimulus/mixture]
            # e.g. send OSC commands to start videos/samplers
            avrenderer.present_next_trial()

            # - getResponse
            # e.g. enable experimenter UI controls,
            #      wait for button press,
            #      log response
            # validResponse=False
            while True:  # validResponse==False:
                window[response_key].set_focus()
                event, values = window.read()
                print(event, values)
                if event == sg.WIN_CLOSED:
                    # can't avoid it so just make sure we save the state
                    print(str(probe_strategy.get_current_estimate()))
                    window.close()
                    return
                if event == 'Next':
                    # validate response
                    if isValidResponse(values[response_key]):
                        # - scoreResponse
                        # may need some conversion from what UI returns and what
                        # the actual result is
                        result = scoreResponse(values[response_key])

                        # - storeTrialResult
                        probe_strategy.store_trial_result(result)

                        break

        # test done so tidy up
        # - stop background video/sound
        window.close()

        print(str(probe_strategy.get_current_estimate()))
        return


if __name__ == '__main__':
    #  TODO: Implement passing config from command line

    run_block(block_config)
