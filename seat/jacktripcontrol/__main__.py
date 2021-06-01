import jacktripcontrol

# parse the command line arguments
parser = jacktripcontrol.JTCArgumentParser()
parser.add_argument("-g", "--gui", action="store_true", default=False,
                    help="Use gui to change settings and start/stop jtc")
parser.add_argument("-k", "--kill", action="store_true", default=False,
                    help="Kill any running jack/jacktrip processes")
args = parser.parse_args()


    

# consume the gui option
use_gui = args.gui
del args.gui

# consume the kill option
do_kill = args.kill
del args.kill



# make the object
jtc = jacktripcontrol.JackTripControl(args)

if do_kill:
    jtc.kill()
else:
    # either launch the gui for user control, or just start and block till ready
    if use_gui:
        gui = jacktripcontrol.Gui(jtc)
        gui.show()
    else:
        print('Starting jacktripcontrol...')
        jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING, daemon=True)
        print('connected!')
        # jtc.start(connect_mode=jacktripcontrol.ConnectMode.NO_CONNECT, daemon=True)
