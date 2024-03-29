import loggedprocess as lp
import time


"""
Creates a process, starts it and gets the output
"""
command_string='wsl sleep -v'
# command_string='python C:/gitwin/alastairhmoore/py-console-gui/count.py'
#command_string='ls C:\\'
command_string='wsl bash -c "while sleep 1;do echo $(date);done"'
command_string='wsl bash -c "count=0;while sleep 1;do count=\$((count+1));echo \$count;done"'
search_string = '3'
max_time = 5


mylp = lp.LoggedProcess(command_string=command_string)
print('Started...')
count = 0
end_time = time.perf_counter() + max_time
while mylp.is_running() and (time.perf_counter() < end_time):
    time.sleep(1)
    count += 1
    print(f'{count}:')
    # print(mylp.get_log())
    if len(search_string)>0 and mylp.output_contains(search_string):
        print(f'found "{search_string}"')
        mylp.stop()

time.sleep(3)

mylp.stop()

# mylp.stop()
# # if len(log)>100:
# #     print('long log')
# # else:
# print(log)


