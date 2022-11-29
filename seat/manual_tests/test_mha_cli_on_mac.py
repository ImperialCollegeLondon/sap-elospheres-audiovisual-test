import avrenderercontrol as avrc

import pathlib
import time

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_directory = pathlib.Path(parent_directory,'manual_tests_data','mha')
    
    # mha stuff
    mha_config = {'base_dir': pathlib.Path(data_directory),
                  'cfg_path': 'mha.cfg',
                  'mha_install_dir': pathlib.Path(pathlib.Path.home(),'git','alastairhmoore','openMHA')}
    mha_cli = avrc.MhaCliMacLocal(mha_config)
    mha_cli.start()
    
    # tascar stuff
    scene_path = pathlib.Path(data_directory, 'moving_source.tsc')
    tascar_config = {'scene_path': scene_path}
    tascar_cli = avrc.TascarCliMacLocal(tascar_config)
    tascar_cli.start()
    
    time.sleep(20)
    
    tascar_cli.stop()
    mha_cli.stop()
    