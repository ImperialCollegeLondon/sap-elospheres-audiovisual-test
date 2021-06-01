import PySimpleGUI as sg
import jacktripcontrol


"""
Test that the metronome plays on the left channel

Assumes that there is no jack infrastructure setup yet
"""
jtc = jacktripcontrol.JackTripControl()
jtc.kill()
print('In a moment, the JackTripControl gui will be presented. Check your settings,\n'
      'press start, wait for status to show connected then close the gui.')
input('Press Enter to proceed')

gui = jacktripcontrol.Gui(jtc)
gui.show()
# input('Press enter to start jtc')

# #
# # jtc.start(connect_mode=jacktripcontrol.ConnectMode.NO_CONNECT)
# jtc.start(connect_mode=jacktripcontrol.ConnectMode.BLOCKING)



# print('Starting jack servers on remote and local machines...')
# print('Wait until consoles indicate that JackTrip connection has been established')
# print('This may take several seconds...')
# input("Press Enter to continue with connecting JackTrip to the local soundcard...")
# jtc.test_metronome_manual()
print('JackTripControl should now be running. Open QJackCtl and check its all ok. \n'
      'press start, wait for status to show connected then close the gui.')
input("When ready, press Enter to test audio with metronome")
# sg.popup('Open QJackCtl and check its all ok. Then close this window to test with metronome')

jtc.test_metronome_manual()

print('Stopping JTC')
jtc.stop()

print('Stopped JTC')
jtc = []
