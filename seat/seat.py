import probestrategy
# import gui

import PySimpleGUI as sg

import time, random
import numpy as np



# def getLayout():
#     """Defines the overall layout of the GUI and keys for the elements"""
#     layout = [[sg.Text('Probe level:'), sg.Text(size=(15,1), key=psKey)],
#               [sg.Input(key='-IN-')],
#               [sg.Button('Next'), sg.Button('Exit')]]

def scoreResponse(response):
    """Temporary function in liu of an extensible approach"""
    #convert a string representing int between 0 and 5 to a fraction
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
        
    if (np.remainder(response,1)!=0):
        print('Not an integer')
        return False
    
    return True
        

def runExperiment():
    
    # settings
    preTrialDelay=(0.2,1)
    
    
    # setup the test
    probeLevel=0.6
    nTrials = 6
    ps = probestrategy.FixedProbeLevel(probeLevel,nTrials)
    
    
    psKey='-ProbeDetails-'
    materialsKey='-Materials-'
    responseKey='-Response-'
    layout = [[sg.Text('Probe level:'), sg.Text(size=(15,1), key=psKey)],
              [sg.Text('Keywords:'),    sg.Text(size=(80,1), key=materialsKey)],
              [sg.Input(key=responseKey,focus=True)],
              [sg.Button('Next')]]
    
    window = sg.Window('SAP ELO-SPHERES AV Test', layout,finalize=True, use_default_focus=False)
    
    # start test
 #    - play background video
 #    - play background audio

    # main loop
    while (ps.isFinished()==False):
    
        # doTrial
        # - getProbeLevel
        thisProbeLevel = ps.getNextProbeLevel()
        
        thisTrialMaterial = random.sample(['Boy', 'Girl', 'Dog', 'Cat', 'Plane','Car',
                                    'Sun','Moon'], k=5)
        
        # - showExperimenterUI
        window[psKey].update(str(thisProbeLevel))
        window[materialsKey].update(str(thisTrialMaterial))
        window[responseKey].update('')
        

        # - prepareTrial
        #     e.g. send OSC commands to set levels of source(s)

        # - pause (random duration between preTrialDelay[0] and preTrialDelay[1])
        time.sleep(preTrialDelay[0]+(preTrialDelay[1]-preTrialDelay[0])*random.random())

        # - [present stimulus/mixture]
            # e.g. send OSC commands to start videos/samplers

        
        # - getResponse
        # e.g. enable experimenter UI controls, wait for button press, log response
        # validResponse=False
        while True: #validResponse==False:
            window[responseKey].set_focus()
            event, values = window.read()
            print(event, values)
            if event == sg.WIN_CLOSED:
                # can't avoid it so just make sure we save the state
                print(str(ps.getCurrentEstimate()))
                window.close()
                return
            if event == 'Next':
                # validate response
                if isValidResponse(values[responseKey]):
                    # - scoreResponse
                    # may need some conversion from what UI returns and what the actual result is
                    result = scoreResponse(values[responseKey])

                    # - storeTrialResult
                    ps.storeTrialResult(result)
                    
                    
                    
                    break
        
    # test done so tidy up
    # - stop background video/sound
    # - 
    window.close()
    
    print(str(ps.getCurrentEstimate()))
    return
      





if __name__ == '__main__':
    runExperiment()