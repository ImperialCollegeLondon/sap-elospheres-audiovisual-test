import argparse
import jacktripcontrol

"""
Convenience script to simply stop jacktripcontrol
"""


if __name__ == '__main__':
    # parse the command line inputs
    jtc = jacktripcontrol.JackTripControl()
    jtc.kill()
    
    