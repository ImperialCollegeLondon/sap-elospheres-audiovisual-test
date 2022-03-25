import avrenderercontrol as avrc

import pathlib
import time

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    scene_path = pathlib.Path(parent_directory,'manual_tests_data','tascar_cli',
                              'moving_source.tsc')
    config = {'scene_path': scene_path}
    tascar_cli = avrc.MacLocal(config)
    tascar_cli.start()
    time.sleep(5)
    tascar_cli.stop()
    