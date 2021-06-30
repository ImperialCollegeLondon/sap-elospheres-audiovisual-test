import datetime
import numpy as np
import pathlib
from pylsl import StreamInfo, StreamOutlet
import socket
import time


def main():
    
    # Define the stream properties + open outlet
    info = StreamInfo('SeatPyLSLTest', 'Markers', 1, 0, 'string', 'myuid_test')
    outlet = StreamOutlet(info)
    
    while True:
        date_string = datetime.datetime.now().strftime("%Y%d%m_%H%M%S")
        print(date_string)
        outlet.push_sample([date_string])
        time.sleep(1)

if __name__ == '__main__':
    main()
