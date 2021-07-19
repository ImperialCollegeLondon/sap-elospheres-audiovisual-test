import datetime
import numpy as np
import pathlib
from pylsl import StreamInfo, StreamOutlet, IRREGULAR_RATE
import random
import socket
import time


def main():
    template_str = 'subject_%p_block_%b_run_%n.xdf'
    subj_str = 's25'
    block_str = '3'
    run_str = '13'
    
    # Define the stream properties + open outlet
    info = StreamInfo('SeatPyLSLTest', 'Markers', 1, 0, 'string', 'myuid_test')
    outlet = StreamOutlet(info)
    
    
     # control LabRecorder
    # lsl_recorder_rc = socket.create_connection(("localhost", 22345))
    lsl_recorder_rc = socket.create_connection(("192.168.1.116", 22345))
    lsl_recorder_rc.sendall(b"update\n")
    time.sleep(2)
    lsl_recorder_rc.sendall(b"select all\n")
    time.sleep(2)

    # lsl_recorder_rc.sendall(b"filename {participant:bob}\n")
    # lsl_recorder_rc.sendall(b"filename {''template':'rcs_block_%b.xdf'}\n")
    # lsl_recorder_rc.sendall(b"filename {'template':'rcs_block_%b.xdf'}\n")
    # lsl_recorder_rc.sendall("filename {template:fixed.xdf}\n".encode(encoding='ascii'))
    # lsl_recorder_rc.sendall("filename {run:20}\n".encode('ascii'))
    # lsl_recorder_rc.sendall(b"filename {run:23}\n")
    # lsl_recorder_rc.sendall("filename {run:24}\n".encode())
    # lsl_recorder_rc.sendall(f"filename {{run:25}}\n".encode())
    lsl_recorder_rc.sendall((f"filename {{template:{template_str}}} " +
                             f"{{participant:{subj_str}}}" +
                             f"{{task:{block_str}}}" +
                             f"{{run:{run_str}}}" +
                             "\n").encode())
    time.sleep(1)

    lsl_recorder_rc.sendall(b"start\n")
    time.sleep(2)
    
    outlet.push_sample(['Start'])
    for i in range(3):
        date_string = datetime.datetime.now().strftime("%Y%d%m_%H%M%S")
        print(date_string)
        outlet.push_sample([date_string])
        time.sleep(1)
    outlet.push_sample(['End'])
    time.sleep(0.5)    
    lsl_recorder_rc.sendall(b"stop\n")
    

def continuous_marker_stream():
     # Define the stream properties + open outlet
    info = StreamInfo('SeatPyLSLTest', 'Markers', 1, IRREGULAR_RATE, 'string', 'myuid_test')
    outlet = StreamOutlet(info)
    while True:
        date_string = datetime.datetime.now().strftime("%Y%d%m_%H%M%S")
        print(date_string)
        outlet.push_sample([date_string])
        time.sleep(1)



if __name__ == '__main__':
    # main()
    continuous_marker_stream()