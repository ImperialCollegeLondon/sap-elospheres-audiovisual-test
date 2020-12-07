import os
import errno

def check_path_is_file(pathlib_path):
    if not pathlib_path.is_file():
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(pathlib_path))
