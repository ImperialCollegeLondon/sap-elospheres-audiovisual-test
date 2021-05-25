import argparse
import time

import jacktripcontrol


"""
Test that gui opens
"""
parser = argparse.ArgumentParser()
parser.add_argument('-d','--asio_soundcard_name', help='device name used by jack to identify the soundcard')
args = parser.parse_args()

jtc = jacktripcontrol.Gui(args)
jtc.show()

time.sleep(4)

jtc.show()