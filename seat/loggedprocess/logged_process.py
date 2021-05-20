import argparse
from datetime import datetime
import numpy as np
import os
import PySimpleGUI as sg
from queue import Queue, Empty
# import shlex
import subprocess
import sys
from threading  import Thread
import time

"""
Extending the simple approach used in main.py, we now want to have a console
per tab.

The main event loop still needs to happen at the top level. But can we wrap
each tab as a class?


Includes code snippets/concepts from
https://stackoverflow.com/a/4896288/3041762
https://stackoverflow.com/a/35900070/3041762

"""


"""
Class to hold all the data about the tab and its process

"""
class TabbedProcess:
    def __init__(self, key, command_string=None, kill_cmd=None, shell=False):
        """
        

        Parameters
        ----------
        key: str
            Title of the tab, also used to identify it
            
        command_string : str
            The command which will be populated in the input field and,
            assuming it is not edited by user, executed

        Returns
        -------
        class instance

        """
        self.num_lines = 30 # number of lines in the console
        element_width = 60
        
        self.proc = None
        self.key = key    
        self.key_cmd = f'{key}.--command--'
        self.shell = shell
        self.key_console = f'{key}.--console--'

        
        self.layout = [[sg.Text(f'This layout has key {self.key}')],
                       [sg.Input(key=self.key_cmd, size=(element_width, 1),
                                 default_text=command_string)],
                       [sg.Text('', key=self.key_console,
                                size=(element_width, self.num_lines),
                                text_color='white', background_color='black')]
                      ]
        
        
    def is_running(self):
        """
        Returns
        -------
        Bool
            True if the process is running. False otherwise.

        """
        if self.proc is None:
            return False
        else:
            return True
  
        
    def start(self, window):
        """
        

        Parameters
        ----------
        window : pysimplegui.Window
            pass reference to the parent so that it can be interrogated.

        Raises
        ------
        ValueError
            If process is already running.

        Returns
        -------
        None.

        """
        
        if self.is_running():
            raise ValueError('A process is already running')
            
    
        
    
        # no process running - so start it
        # - modify envionment so we get unbuffered output from pipe
        my_env = os.environ.copy()
        my_env["PYTHONUNBUFFERED"]='1'
        
        # - split command
        #   conventional approach doesn't handle windows paths
        #   cmd = shlex.split(window[key_cmd].get())
        cmd = cmdline_split(window[self.key_cmd].get())
        # print(cmd)
        try:
            # start the process
            self.proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    env=my_env,
                                    shell=self.shell,
                                    bufsize=1)
            
            # attempt to run using pythonw as a background process
            # this prevents console windows poping up, but can't terminate the
            # wsl process and on windows jack doesn't even start
            # startupinfo = subprocess.STARTUPINFO()
            # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # self.proc = subprocess.Popen(cmd,
            #                         stdout=subprocess.PIPE,
            #                         stderr=subprocess.STDOUT,
            #                         text=True,
            #                         env=my_env,
            #                         shell=self.shell,
            #                         startupinfo=startupinfo,
            #                         bufsize=1)
            # setup mechanism for reading output
            self.q = Queue()
            self.t = Thread(target=enqueue_output,
                            args=(self.proc.stdout, self.q))
            self.t.daemon = True # thread dies with the program
            self.t.start()

           # clear the console
            window[self.key_console].Update('')
        except Exception as e:
            # things could go wrong - use the gui's console display
            # to make it more user friendly
            print(e)
            window[self.key_console].Update(value=repr(e))


    def stop(self):
        """
        Ends the running process

        Raises
        ------
        RuntimeError
            If process fails to stop.

        Returns
        -------
        None.

        """
        if self.is_running():
            # print(f'{self.key}: stop before stdout.close()')
            # self.proc.stdout.close()
            # print(f'{self.key}: stop after stdout.close()')
            if self.proc.poll() is None:
                # print(f'{self.key}: stop before proc.terminate()')
                self.proc.terminate()
                # print(f'{self.key}: stop after proc.terminate()')
                time.sleep(0.5)
                
            if self.proc.poll() is None:
                # print(f'{self.key}: stop before proc.kill()')
                self.proc.kill()
                # print(f'{self.key}: stop after proc.kill()')
                time.sleep(0.5)
                
            if self.proc.poll() is None:
                # print(f'{self.key}: stop process didnt die')
                raise RuntimeError("Process didn't die")

            self.proc = None


    def update(self, window):
        """
        

        Parameters
        ----------
        window : pysimplegui.Window
            pass reference to the parent so that it can be updated.

        Returns
        -------
        None.

        """
        if self.is_running():
            if self.proc.poll() is None: 
                # read line without blocking
                try:  
                    newtext = self.q.get_nowait() # or q.get(timeout=.1)
                except Empty:
                    pass
                else: # got line
                    # new text to add
                    oldtext = window[self.key_console].get().splitlines()
                    lines = oldtext + [newtext]
                    lines = lines[-self.num_lines:]
                    window[self.key_console].Update(value='\n'.join(lines))

            else:
                # process has finished - reset GUI
                self.proc = None
                
    def output_contains(self, window, search_string): 
        for line in window[self.key_console].get().splitlines():
            if search_string in line:
                return True
        return False
                
                
def cmdline_split(s, platform='this'):
    """Multi-platform variant of shlex.split() for command-line splitting.
    For use with subprocess, for argv injection etc. Using fast REGEX.

    platform: 'this' = auto from current platform;
              1 = POSIX; 
              0 = Windows/CMD
              (other values reserved)
              
    posted at https://stackoverflow.com/a/35900070/3041762
    (Licence: CC BY-SA 3.0)
    """
    import re
    
    if platform == 'this':
        platform = (sys.platform != 'win32')
    if platform == 1:
        RE_CMD_LEX = r'''"((?:\\["\\]|[^"])*)"|'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'"\\&|<>]+)|(\s+)|(.)'''
    elif platform == 0:
        RE_CMD_LEX = r'''"((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)'''
    else:
        raise AssertionError('unkown platform %r' % platform)

    args = []
    accu = None   # collects pieces of one arg
    for qs, qss, esc, pipe, word, white, fail in re.findall(RE_CMD_LEX, s):
        if word:
            pass   # most frequent
        elif esc:
            word = esc[1]
        elif white or pipe:
            if accu is not None:
                args.append(accu)
            if pipe:
                args.append(pipe)
            accu = None
            continue
        elif fail:
            raise ValueError("invalid or incomplete shell string")
        elif qs:
            word = qs.replace('\\"', '"').replace('\\\\', '\\')
            if platform == 0:
                word = word.replace('""', '"')
        else:
            word = qss   # may be even empty; must be last

        accu = (accu or '') + word

    if accu is not None:
        args.append(accu)

    return args


def enqueue_output(out, queue):
    """
    Function for pulling output from spawned process and adding it to a queue
    This function is run on a separate thread to avoid blocking the main thread
    
    Based on https://stackoverflow.com/a/4896288/3041762

    """
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
    except ValueError:
        # close the pipe raises this exception and so ends the thread
        pass