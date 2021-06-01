import argparse
import jacktripcontrol

"""
Convenience script to simply start jacktripcontrol
"""


if __name__ == '__main__':
    # parse the command line inputs
    parser = jacktripcontrol.JTCArgumentParser()
    args = parser.parse_args()
    jtc = jacktripcontrol.JackTripControl(args)
    jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING, daemon=True)
    print('Ready!')
    
    