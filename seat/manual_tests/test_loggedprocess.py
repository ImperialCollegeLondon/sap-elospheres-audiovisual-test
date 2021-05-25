import loggedprocess as lp
import time


"""
Creates a process, starts it and gets the output
"""
command_string='wsl sleep -v'
# command_string='python C:/gitwin/alastairhmoore/py-console-gui/count.py'
#command_string='ls C:\\'
shell = False
mylp = lp.LoggedProcess(command_string=command_string, shell=shell)
mylp.start()
print('Started...')
count = 0
while mylp.is_running():
    time.sleep(1)
    count += 1
    print(f'{count}:')
    print(mylp.get_log())

# mylp.stop()
# # if len(log)>100:
# #     print('long log')
# # else:
# print(log)
