import argparse
import PySimpleGUI as sg

import jacktripcontrol

def gui():
    """
    gui
    Creates a graphical user interface to control starting and stopping jacktrip

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    """
    print(f'Using gui version')
    jtc= jacktripcontrol.JackTripControl()

    button_keys = ['Start' , 'Connect', 'Disconnect', 'Stop']  
    button_actions = {'Start': jtc.start,
                      'Connect': jtc.connect,
                      'Disconnect': jtc.disconnect,
                      'Stop': jtc.stop} 
    layout = [[sg.Button(key, key=key, size=(8,1)) for key in button_keys]]
    window = sg.Window('JackTripControl', layout,
                                keep_on_top=False,
                                return_keyboard_events=False,
                                # use_default_focus=False,
                                finalize=True)

    while True:             # Event Loop
        event, values = window.Read()
        # print(event, values)
        
        if event == sg.WIN_CLOSED:
            window.close()
            return
        elif event in button_keys:
            print(f'{event} button pressed')
            button_actions[event]()

    return




def main():
    """
    main
    
    sets up jacktrip using only the command line/console to control timings
    """
    print('Starting jack servers on remote and local machines...')
    print('This may take several seconds...')
    jtc = jacktripcontrol.JackTripControl()
    jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING)
    print('Ready!')
    return


if __name__ == '__main__':
    # parse the command line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="conditions file (.csv)")
    parser.add_argument("-g", "--gui", action="store_true",
                        help="Use gui. closing will teardown jack/jacktrip")
    # parser.add_argument("-o", "--out-dir",
    #                     help="output directory for logs/results")
    args = parser.parse_args()
    print(args)
    
    if args.gui:
        gui()
    else:
        main()
    
    