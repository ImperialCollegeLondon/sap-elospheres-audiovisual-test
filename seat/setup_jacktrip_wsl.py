import argparse
import jacktripcontrol

"""
Convenience script to configure jacktripcontrol
"""


if __name__ == '__main__':
    # parse the command line inputs
    parser = jacktripcontrol.JTCArgumentParser()
    args = parser.parse_args()
    jtc = jacktripcontrol.JackTripControl(args)
    gui = jacktripcontrol.Gui(jtc)
    gui.show()
    jtc.stop()
