from abc import ABC, abstractmethod
import confuse
import os
import pathlib
import stat
import subprocess
import time

import util
# TODO: Implementations are very similar - scope to avoid repetition

class TascarCli(ABC):
    """
    Abstract base class to define the interface

    scene_path is the .tsc file

    ipaddress can be set at intialisation  is read-only
    """
    def __init__(self, config):
        self.scene_path = config["scene_path"]
        self.tascar_pid_as_str = ''
        self._ip_address = '127.0.0.1'
        self.osc_port = 9877


    @abstractmethod
    def start(self):
        """
        Launches the tascar_cli with already supplied scene

        Raises exception if it doesn't work
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Terminate the tascar_cli process
        """
        pass

    """
    To protect ipaddress define it as a property
    """
    @property
    def ip_address(self):
        """The ipaddress to use for communicating with TASCAR using OSC"""
        return self._ip_address



class TascarCliMacLocal(TascarCli):
    def __init__(self, config):
        super().__init__(config)

    def start(self):
        pathlib_path = pathlib.Path(self.scene_path)
        util.check_path_is_file(pathlib_path)

        cli_command = f'tascar_cli {str(pathlib_path)}'
        # cli_command = f'tascar {str(pathlib_path)}' # for debugging purposes, we can show the gui
        print(cli_command)
        self.tascar_process = subprocess.Popen(cli_command, shell=True)

        # subprocess.CREATE_NEW_CONSOLE not available on mac
        # using solution from https://stackoverflow.com/a/58110482/3041762
        # sh_file = 'cli_command.sh'
#         with open(sh_file, "w") as f:
#             f.write(f"#!/bin/sh\n{cli_command}\n")
#             os.chmod(sh_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
#         self.tascar_process = subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal', sh_file], shell=False)


        # give tascar a chance to start
        time.sleep(0.3)

        # check process is running
        if self.tascar_process.poll() is not None:
            # oh dear, it's not running!
            # try again with settings which will allow us to debug
            self.tascar_process = subprocess.Popen(cli_command, shell=True,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True)
            # self.tascar_process = subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal', sh_file],
#                 shell=False,
#                 stderr=subprocess.PIPE, stdout=subprocess.PIPE,
#                 text=True)
            outs, errs = self.tascar_process.communicate()
            print('stdout:')
            if outs is not None:
                print(outs)
                # for line in outs:
                #     print(line)
            print('stderr:')
            if errs is not None:
                print(errs)

        # get the process pid in wsl land
        cli_command = 'pidof tascar_cli'
        try:
            result = subprocess.run(cli_command,
                                    capture_output=True,
                                    check=True,
                                    text=True,
                                    shell=True)
            self.tascar_pid_as_str = result.stdout.rstrip()
            print('tascar_cli running with pid: ' + self.tascar_pid_as_str)

        except subprocess.CalledProcessError:
            # we got an error, which means we couldn't get the pid
            # nothing to be done but exit gracefully
            print('couldn''t get pid of tascar_cli')
            raise RuntimeError("probably tascar_cli failed to start")


    def stop(self):
        # end tascar_cli process directly using linux kill
        # this avoids audio glitches
        cli_command = f'kill {self.tascar_pid_as_str}'
        # print(cli_command)
        subprocess.run(cli_command, shell=True)

        # make sure it really has finished
        if self.tascar_process.poll() is None:
            self.tascar_process.terminate()


class TascarCliWsl(TascarCli):
    def __init__(self, config):
        super().__init__(config)

        app_name = 'tascar_cli_wsl'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        tascar_ipaddress = self.moduleConfig['tascar']['ipaddress'].get(str)
        print('config tascar.ipaddress:' + tascar_ipaddress)
        if not util.is_valid_ipaddress(tascar_ipaddress):
            env_variable_name = self.moduleConfig['tascar']['ipenvvariable'] \
                .get(str)
            filename = os.environ.get(env_variable_name)
            print('Reading tascar IP address from ' + filename)
            with open(filename, "r") as myfile:
                tascar_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(env_variable_name, tascar_ipaddress))
            if not util.is_valid_ipaddress(tascar_ipaddress):
                # failed to get a valid ipaddress
                print(tascar_ipaddress)
                raise ValueError
            # store it
            self._ip_address = tascar_ipaddress


    def start(self):
        pathlib_path = pathlib.Path(self.scene_path)
        util.check_path_is_file(pathlib_path) # windows path
        wsl_path = util.convert_windows_path_to_wsl(pathlib_path)

        cli_command = 'wsl ' \
            + '-u root bash -c \"/usr/bin/tascar_cli ' \
            + str(wsl_path) \
            + '\"'
        # print(cli_command)
        self.tascar_process = subprocess.Popen(
            cli_command, creationflags=subprocess.CREATE_NEW_CONSOLE)

        # give tascar a chance to start
        time.sleep(0.3)

        # check process is running
        if self.tascar_process.poll() is not None:
            # oh dear, it's not running!
            # try again with settings which will allow us to debug
            self.tascar_process = subprocess.Popen(
                cli_command, creationflags=subprocess.CREATE_NEW_CONSOLE,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True)
            outs, errs = self.tascar_process.communicate()
            print('stdout:')
            if outs is not None:
                print(outs)
                # for line in outs:
                #     print(line)
            print('stderr:')
            if errs is not None:
                print(errs)

        # get the process pid in wsl land
        cli_command = 'wsl -u root bash -c \"' \
            + 'pidof tascar_cli' \
            + '\"'
        try:
            result = subprocess.run(cli_command,
                                    capture_output=True,
                                    check=True,
                                    text=True)
            self.tascar_pid_as_str = result.stdout.rstrip()
            print('tascar_cli running with pid: ' + self.tascar_pid_as_str)

        except subprocess.CalledProcessError:
            # we got an error, which means we couldn't get the pid
            # nothing to be done but exit gracefully
            print('couldn''t get pid of tascar_cli')
            raise RuntimeError("probably tascar_cli failed to start")


    def stop(self):
        # end tascar_cli process directly using linux kill
        # this avoids audio glitches
        # end tascar_cli process directly using linux kill
        # this avoids audio glitches
        cli_command = 'wsl ' \
            + '-u root bash -c \"kill ' \
            + self.tascar_pid_as_str \
            + '\"'
        # print(cli_command)
        subprocess.run(cli_command)

        # make sure it really has finished
        if self.tascar_process.poll() is None:
            self.tascar_process.terminate()
