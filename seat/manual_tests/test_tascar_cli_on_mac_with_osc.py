import avrenderercontrol as avrc

import pathlib
import time
import util
from pythonosc import udp_client


if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    scene_path = pathlib.Path(parent_directory,'manual_tests_data','tascar_cli',
                              'moving_source.tsc')
    config = {'scene_path': scene_path}
    
    # we know it's MacLocal so use know ipaddress
    tascar_ipaddress = '127.0.0.1'
    tascar_osc_port = 9877
    if not util.is_valid_ipaddress(tascar_ipaddress):
        raise ValueError("IP address")
    
    # osc stuff - needs to match tsc file contents
    scene_name = 'main'
    source_name = 'src'
    
    # start tascar
    tascar_cli = avrc.MacLocal(config)
    tascar_cli.start()
    time.sleep(2)
    
    tascar_osc = udp_client.SimpleUDPClient(tascar_ipaddress, tascar_osc_port)
    
    # alternate mute/unmute the source
    
    for rep in range(2):
        tascar_osc.send_message(f'/{scene_name}/{source_name}/mute', [1])
        time.sleep(1)
        tascar_osc.send_message(f'/{scene_name}/{source_name}/mute', [0])
        time.sleep(2)
        
    
    tascar_cli.stop()
    