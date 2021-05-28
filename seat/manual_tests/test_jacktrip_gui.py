import time

import jacktripcontrol


"""
Test that gui opens and reopens
"""
jtc = jacktripcontrol.JackTripControl()
gui = jacktripcontrol.Gui(jtc)
gui.show()
time.sleep(2)
gui.show()