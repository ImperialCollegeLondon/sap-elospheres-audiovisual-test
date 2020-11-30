import jacktripcontrol

print('Starting jack servers on remote and local machines...')
print('Wait until consoles indicate that JackTrip connection has been established')
print('This may take several seconds...')

jtc = jacktripcontrol.JackTripControl()
jtc.start()
input("Press Enter to continue with connecting JackTrip to the local soundcard...")
jtc.connect()
