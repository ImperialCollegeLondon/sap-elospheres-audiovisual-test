import os
import pathlib
import subprocess
import sys
import tempfile
import time



"""
Wrapper for subprocess.Popen to take care of writting and accessing a log file.

Includes extra options to allow process to continue even after this object is
is garbage collected

Includes code snippet from https://stackoverflow.com/a/35900070/3041762 to
split the supplied command_string
"""
class LoggedProcess:
    def __init__(self, command_string=None,
                 stop_command_string=None,
                 logpath=None,
                 delete_log_on_exit=None,
                 detach_on_exit=False):
        """
        Create a subprocess using Popen

        Parameters
        ----------
        command_string : str
            The command which will be executed
        stop_command_string: str
            The command which will be executed (in addition to proc.terminate())
            when stop() is called. This is helpful for wsl or when the called
            process spawns its own processes.
        logpath: str
            specify a logfile to save the console output to
        delete_log_on_exit: bool
            defaults to True if logpath is None and False if logpath is given
        detach_on_exit: bool
            allows process to continue when object is deleted

        Returns
        -------
        class instance

        """

        if logpath is None:
            fd, self.logpath = tempfile.mkstemp()
            self.f = open(fd,'w')
            self.delete_log_on_exit = True
        else:
            self.logpath = pathlib.Path(logpath)
            self.f = open(self.logpath,'w')
            self.delete_log_on_exit = False
        # default determined above, override if specified    
        if delete_log_on_exit is not None:
            self.delete_log_on_exit = delete_log_on_exit
        
        self.set_detach_on_exit(detach_on_exit)

        
        # start it immediatelly
        # - modify envionment so we get unbuffered output from pipe
        my_env = os.environ.copy()
        my_env["PYTHONUNBUFFERED"]='1'
        
        # - split command
        #   conventional approach doesn't handle windows paths
        #   cmd = shlex.split(self.command_string)
        cmd = cmdline_split(command_string)
        # print(cmd)
        
        self.stop_cmd = None
        if stop_command_string is not None:
            self.stop_cmd = cmdline_split(stop_command_string)

        
        # start the process
        # print(f'Executing command: {cmd}')
        try:
            self.proc = subprocess.Popen(cmd,
                                    stdin=subprocess.DEVNULL,
                                    stdout=self.f,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    env=my_env,
                                    bufsize=1)
        except (IOError, ValueError) as err:
            self.f.write([f'Attempt to run {cmd} failed',
                        f'{err}'])

    def set_detach_on_exit(self, detach_on_exit):
        self.detach_on_exit = detach_on_exit

        
    def stop(self):
        """
        Terminates the process. If child processes have been spawned it may be
        necessary to supply the stop_cmd argument at object intialisation

        Returns
        -------
        None.

        """
        self.proc.terminate()
        if self.stop_cmd is not None:
            subprocess.call(self.stop_cmd)

         
    def get_log(self):
        """
        Returns the full console log - stdout and stderr are merged

        Returns
        -------
        log : str
            The log

        """
        with open(self.logpath) as f:
            log = f.read()
        return log

    def output_contains(self, search_string):
        """
        Basic implementation which searches for the given string in the log

        Parameters
        ----------
        search_string : str
            The string to look for

        Returns
        -------
        bool
            True if string is found.

        """
        for line in self.get_log().splitlines():
            if search_string in line:
                return True
        return False

    def __del__(self):
        if self.detach_on_exit:
            if self.delete_log_on_exit:
                print(f'Process detached...log file {self.logpath} not deleted')
        else:
            # print(f'Stopping process in finalizer')
            self.stop()
            self.f.close()
            if self.delete_log_on_exit:
                time.sleep(0.01)
                try:
                    os.remove(self.logpath)
                except OSError as error:
                    print(f'log file at {self.logpath} was not removed')
            
    def is_running(self):
        """
        Returns
        -------
        Bool
            True if the process is running. False otherwise.

        """
        if self.proc is None:
            # print('in process.is_running() proc is None')
            return False
        
        if self.proc.poll() is not None:
            # print('in process.is_running() .poll() is not None...process seems to have finished...')
            # self.proc = None
            return False
        
        return True

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