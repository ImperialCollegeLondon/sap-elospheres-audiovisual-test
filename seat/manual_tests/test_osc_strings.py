import pathlib
from pythonosc import udp_client
import numpy as np
import time


if __name__ == '__main__':
    """
    For ease, manually run:
    
    tascar /Users/amoore1/git/ImperialCollegeLondon/sap-elospheres-audiovisual-test/seat/demo_data/03_TargetSpeechTwoMaskers_v2_mac/tascar_scene.tsc
    
    TODO: Automate this
    """
    
    
    # setup the client
    ipaddress = '127.0.0.1'
    # ipaddress = '192.168.1.157'
    oscport = 9877
    osc_client = udp_client.SimpleUDPClient(ipaddress, oscport)

    markers = ['marker1','second marker', '3', '4.0', '{"key": "val"}']
    
    osc_client.send_message("/session_trialid", ['test_osc_strings'])
    osc_client.send_message("/session_outputdir", ['../../local_unversioned_tmp_files'])
    osc_client.send_message("/session_start", [])
    time.sleep(1.0)    
    
    # for ii in range(4):
#         osc_client.send_message("/background_noise/pink/mute", [int(True)])
#         osc_client.send_message("/log/mute", [int(True)])
#
#         time.sleep(1.0)
#         osc_client.send_message("/background_noise/pink/mute", [int(False)])
#         osc_client.send_message("/log/mute", [int(False)])
#         time.sleep(1.0)
            
    # remove the idle video
    for marker in markers:
        osc_client.send_message("/seat_marker", [marker])
        osc_client.send_message("/main/src/mute", [int(mute)])
        mute = not mute
        time.sleep(1.0)
    
    osc_client.send_message("/seat_marker", ['stop session'])    
    osc_client.send_message("/session_stop", [])
        

    

        