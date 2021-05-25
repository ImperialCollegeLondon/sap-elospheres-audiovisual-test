import jacktripcontrol

"""
Test that the metronome plays on the left channel

Assumes that there is no jack infrastructure setup yet
"""
jtc = jacktripcontrol.JackTripControl()
input('Press enter to start jtc')
jtc.start(block=True)

# print('Starting jack servers on remote and local machines...')
# print('Wait until consoles indicate that JackTrip connection has been established')
# print('This may take several seconds...')
# input("Press Enter to continue with connecting JackTrip to the local soundcard...")
# jtc.test_metronome_manual()

input("Open QJackCtl and check its all ok")
print('Stopping JTC')
jtc.stop()

print('Stopped JTC')
jtc = []
