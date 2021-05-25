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
class LoggedProcess:
    def __init__(self, command_string=None, shell=False):
        """
        

        Parameters
        ----------
        command_string : str
            The command which will be executed

        Returns
        -------
        class instance

        """
        self.maximum_history = 2000 # number of lines of log to keep     
        self.proc = None
        self.command_string = command_string
        self.shell = shell
        self.log = []
        
        
    def is_running(self):
        """
        Returns
        -------
        Bool
            True if the process is running. False otherwise.

        """
        if self.proc is None:
            return False
        
        if self.proc.poll() is not None:
            # print('process seems to have finished...')
            self.proc.stdout.close()
            self.proc = None
            return False
        
        return True
  

    def start(self):
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
        #   cmd = shlex.split(self.command_string)
        cmd = cmdline_split(self.command_string)
        # print(cmd)

        # clear the log
        self.log = []
        
        # start the process
        # print(f'Executing command: {cmd}')
        try:
            self.proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    env=my_env,
                                    shell=self.shell,
                                    bufsize=1)
        except (IOError, ValueError) as err:
            self.log = [f'Attempt to run {cmd} failed',
                        f'{err}']
            return

        self.q = Queue()
        self.t = Thread(target=enqueue_output,
                        args=(self.proc.stdout, self.q))
        # self.t = Thread(target=self.update_log,
        #                 args=(self.proc.stdout, self.log))
        self.t.daemon = True # thread dies with the program
        self.t.start()
        
        self.t_log = Thread(target=service_queue,
                            args=(self.q, self.log))
        self.t_log.daemon = True
        self.t_log.start()





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
            if self.proc.poll() is None:
                self.proc.terminate()
                time.sleep(0.5)
                
            if self.proc.poll() is None:
                self.proc.kill()
                time.sleep(0.5)
                
            if self.proc.poll() is None:
                raise RuntimeError("Process didn't die")

            self.proc = None


    def get_log(self):
        """

        Returns
        -------
        str
            the log as a printable string.

        """
        # self.refresh_log()
        # return '\n'.join(self.log)
        return ''.join(self.log)
            
    def output_contains(self, search_string):
        # self.refresh_log()
        for line in self.log:
            if search_string in line:
                return True
        return False


def enqueue_output(out, queue):
    """
    Function for pulling output from spawned process and adding it to a queue
    This function is run on a separate thread to avoid blocking the main thread
    
    Based on https://stackoverflow.com/a/4896288/3041762

    """
    try:
        for line in iter(out.readline, b''):
            if line != '':
                queue.put(line)
    # out.close()
    except ValueError:
        pass
        # print('ValueError in enqueue_output suggests pipe was closed')
        
        

def service_queue(queue, log):
    """
    Causes log for process to be updated

    Returns
    -------
    None.

    """
    # read line without blocking
    while True:
        try:  
            newtext = queue.get_nowait() # or q.get(timeout=.1)
        except Empty:
            # done = True
            # print('Empty - done')
            pass
        else: # got line
            # new text to add
            log += [newtext]


                
                
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
