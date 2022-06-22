import pathlib
from pythonosc import udp_client
import numpy as np
import time


if __name__ == '__main__':
    # setup the client
    ipaddress = '127.0.0.1'
    ipaddress = '192.168.1.157'
    oscport = 9877
    osc_client = udp_client.SimpleUDPClient(ipaddress, oscport)
    mute = True

    markers = ['marker1','second marker', '3', '4.0', 'marker 5']
    
    osc_client.send_message("/session_trialid", ['marker_test'])
    osc_client.send_message("/session_start", [])
    time.sleep(1.0)    
    
    # remove the idle video
    for marker in markers:
        osc_client.send_message("/marker", [marker])
        osc_client.send_message("/main/src/mute", [int(mute)])
        mute = not mute
        time.sleep(1.0)
    osc_client.send_message("/session_stop", [])
        