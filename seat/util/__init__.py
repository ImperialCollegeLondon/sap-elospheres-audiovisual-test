import errno
import importlib
import ipaddress
import os
import subprocess


def check_path_is_file(pathlib_path):
    if not pathlib_path.is_file():
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(pathlib_path))

def is_valid_ipaddress(address_to_test):
    """Private function to check validity of an ip address"""
    try:
        parsed_address = ipaddress.ip_address(address_to_test)
        print('parsed address:' + str(parsed_address))
        return True
    except ValueError as err:
        print(err)
        print('Invalid address:', address_to_test)
        return False

def convert_windows_path_to_wsl(pathlib_win_path):
    wsl_command = ("wsl bash -c \"wslpath '"
                   + str(pathlib_win_path)
                   + "'\"")
    try:
        result = subprocess.run(wsl_command,
                                capture_output=True,
                                check=True,
                                text=True)
        return result.stdout.rstrip()

    except subprocess.CalledProcessError as error:
        print('Path conversion using wslpath failed')
        print(wsl_command)
        raise error

def wsl_user_home_dir():
    wsl_command = ("wsl bash -c 'echo $HOME'")
    try:
        result = subprocess.run(wsl_command,
                                capture_output=True,
                                check=True,
                                text=True)
        return result.stdout.rstrip()

    except subprocess.CalledProcessError as error:
        print('Path conversion using wslpath failed')
        print(wsl_command)
        raise error

def instance_builder(config):
    """ Returns a class instance given a dict with keys
        class: fully qualified class name
        settings: dict of parameters which the class constructor takes
    """
    module_name, class_name = config["class"].rsplit(".", 1)
    callable_class_constructor = getattr(importlib.import_module(module_name),
                                         class_name)
    return callable_class_constructor(config["settings"])
