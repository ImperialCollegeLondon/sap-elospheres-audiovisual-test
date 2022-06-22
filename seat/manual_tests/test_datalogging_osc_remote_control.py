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

    
    osc_client.send_message("/session_trialid", ['remote_control_test'])
    osc_client.send_message("/session_start", [])
    time.sleep(3.0)    
    osc_client.send_message("/session_stop", [])
        