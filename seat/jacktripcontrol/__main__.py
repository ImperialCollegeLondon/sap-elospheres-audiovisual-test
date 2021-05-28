import jacktripcontrol

# parse the command line arguments
parser = jacktripcontrol.JTCArgumentParser()
parser.add_argument("-g", "--gui", action="store_true", default=False,
                    help="Use gui to change settings and start/stop jtc")
args = parser.parse_args()

# consume the gui option
use_gui = args.gui
del args.gui

# make the object
jtc = jacktripcontrol.JackTripControl(args)

# either launch the gui for user control, or just start and block till ready
if use_gui:
    gui = jacktripcontrol.Gui(jtc)
    gui.show()
else:
    jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING)
