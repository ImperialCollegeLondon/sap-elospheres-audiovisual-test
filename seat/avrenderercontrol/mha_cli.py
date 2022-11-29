from abc import ABC, abstractmethod
import confuse
import os
import pathlib
import stat
import subprocess
import time

import util
# TODO: Implementations are very similar - scope to avoid repetition

class MhaCli(ABC):
    """
    Abstract base class to define the interface

    scene_path is the .tsc file

    ipaddress can be set at intialisation  is read-only
    """
    def __init__(self, config):
        self.base_dir = config["base_dir"]
        self.cfg_path = config["cfg_path"]
        self.mha_install_dir = config["mha_install_dir"]
        # TODO: allow this to passed in the config
        if "load_wait_time" in config:
            self.load_wait_time = config["load_wait_time"]
        else:
            self.load_wait_time = 3
        self.mha_pid_as_str = ''
        self._ip_address = '127.0.0.1'
        self.osc_port = 33337


    @abstractmethod
    def start(self):
        """
        Launches the mha cli with already supplied configuration

        Raises exception if it doesn't work
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Terminate the mha process
        """
        pass

    """
    To protect ipaddress define it as a property
    """
    @property
    def ip_address(self):
        """The ipaddress to use for communicating with mha using OSC"""
        return self._ip_address



class MhaCliMacLocal(MhaCli):
    def __init__(self, config):
        super().__init__(config)

    def start(self):
        base_dir = pathlib.Path(self.base_dir)
        cfg_path = pathlib.Path(self.cfg_path)
        util.check_path_is_file(pathlib.Path(base_dir, cfg_path))
        
        thismha_path = pathlib.Path(self.mha_install_dir,'bin','thismha.sh')
        util.check_path_is_file(thismha_path)
        
        cli_command = f'source {thismha_path} && cd {str(base_dir)} && mha ?read:{str(cfg_path)} io.name=mha port={self.osc_port} cmd=start'
        print(cli_command)
        self.mha_process = subprocess.Popen(cli_command, shell=True)

        # subprocess.CREATE_NEW_CONSOLE not available on mac
        # using solution from https://stackoverflow.com/a/58110482/3041762
        # sh_file = 'cli_command.sh'
#         with open(sh_file, "w") as f:
#             f.write(f"#!/bin/sh\n{cli_command}\n")
#             os.chmod(sh_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
#         self.mha_process = subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal', sh_file], shell=False)


        # give mha a chance to start
        time.sleep(self.load_wait_time)

        # check process is running
        if self.mha_process.poll() is not None:
            # oh dear, it's not running!
            # try again with settings which will allow us to debug
            self.mha_process = subprocess.Popen(cli_command, shell=True,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True)
            # self.mha_process = subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal', sh_file],
#                 shell=False,
#                 stderr=subprocess.PIPE, stdout=subprocess.PIPE,
#                 text=True)
            outs, errs = self.mha_process.communicate()
            print('stdout:')
            if outs is not None:
                print(outs)
                # for line in outs:
                #     print(line)
            print('stderr:')
            if errs is not None:
                print(errs)

        # get the process pid
        cli_command = 'pidof mha'
        try:
            result = subprocess.run(cli_command,
                                    capture_output=True,
                                    check=True,
                                    text=True,
                                    shell=True)
            self.mha_pid_as_str = result.stdout.rstrip()
            print('mha running with pid: ' + self.mha_pid_as_str)

        except subprocess.CalledProcessError:
            # we got an error, which means we couldn't get the pid
            # nothing to be done but exit gracefully
            print('couldn''t get pid of mha')
            raise RuntimeError("probably mha failed to start")


    def stop(self):
        # end mha process directly using linux kill
        # this avoids audio glitches
        cli_command = f'kill {self.mha_pid_as_str}'
        # print(cli_command)
        subprocess.run(cli_command, shell=True)

        # make sure it really has finished
        if self.mha_process.poll() is None:
            self.mha_process.terminate()


class MhaCliWsl(MhaCli):
    def __init__(self, config):
        raise NotImplemented
        # TODO: Go through the code below and properly adapt it to mha - this is just tascar_cli with find/replace
        super().__init__(config)

        app_name = 'mha_wsl'
        self.moduleConfig = confuse.Configuration(app_name, __name__)
        mha_ipaddress = self.moduleConfig['mha']['ipaddress'].get(str)
        print('config mha.ipaddress:' + mha_ipaddress)
        if not util.is_valid_ipaddress(mha_ipaddress):
            env_variable_name = self.moduleConfig['mha']['ipenvvariable'] \
                .get(str)
            filename = os.environ.get(env_variable_name)
            print('Reading mha IP address from ' + filename)
            with open(filename, "r") as myfile:
                mha_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(env_variable_name, mha_ipaddress))
            if not util.is_valid_ipaddress(mha_ipaddress):
                # failed to get a valid ipaddress
                print(mha_ipaddress)
                raise ValueError
            # store it
            self._ip_address = mha_ipaddress


    def start(self):
        pathlib_path = pathlib.Path(self.scene_path)
        util.check_path_is_file(pathlib_path) # windows path
        wsl_path = util.convert_windows_path_to_wsl(pathlib_path)

        cli_command = 'wsl ' \
            + '-u root bash -c \"/usr/bin/mha ' \
            + str(wsl_path) \
            + '\"'
        # print(cli_command)
        self.mha_process = subprocess.Popen(
            cli_command, creationflags=subprocess.CREATE_NEW_CONSOLE)

        # give mha a chance to start
        time.sleep(self.load_wait_time)

        # check process is running
        if self.mha_process.poll() is not None:
            # oh dear, it's not running!
            # try again with settings which will allow us to debug
            self.mha_process = subprocess.Popen(
                cli_command, creationflags=subprocess.CREATE_NEW_CONSOLE,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True)
            outs, errs = self.mha_process.communicate()
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
            + 'pidof mha' \
            + '\"'
        try:
            result = subprocess.run(cli_command,
                                    capture_output=True,
                                    check=True,
                                    text=True)
            self.mha_pid_as_str = result.stdout.rstrip()
            print('mha running with pid: ' + self.mha_pid_as_str)

        except subprocess.CalledProcessError:
            # we got an error, which means we couldn't get the pid
            # nothing to be done but exit gracefully
            print('couldn''t get pid of mha')
            raise RuntimeError("probably mha failed to start")


    def stop(self):
        # end mha process directly using linux kill
        # this avoids audio glitches
        # end mha process directly using linux kill
        # this avoids audio glitches
        cli_command = 'wsl ' \
            + '-u root bash -c \"kill ' \
            + self.mha_pid_as_str \
            + '\"'
        # print(cli_command)
        subprocess.run(cli_command)

        # make sure it really has finished
        if self.mha_process.poll() is None:
            self.mha_process.terminate()
