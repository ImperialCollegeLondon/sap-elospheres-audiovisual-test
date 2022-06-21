import avrenderercontrol as avrc

import pathlib
import time
import util
from pythonosc import udp_client


if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    scene_path = pathlib.Path(parent_directory,'demo_data','03_TargetSpeechTwoMaskers_v2_mac',
                              'tascar_scene.tsc')
    config = {'scene_path': scene_path}
    
    # we know it's MacLocal so use know ipaddress
    tascar_ipaddress = '127.0.0.1'
    tascar_osc_port = 9877
    if not util.is_valid_ipaddress(tascar_ipaddress):
        raise ValueError("IP address")
    
    sampler_ipaddress = '239.255.1.7'
    sampler1_port = 9001
    sampler3_port = 9005
    
    # osc stuff - needs to match tsc file contents
    scene_name = 'main'
    source1_name = 'source1'
    source3_name = 'source3'
    
    
    # start tascar
    tascar_cli = avrc.MacLocal(config)
    tascar_cli.start()
    time.sleep(2)
    
    tascar_osc = udp_client.SimpleUDPClient(tascar_ipaddress, tascar_osc_port)
    sampler1_osc = udp_client.SimpleUDPClient(sampler_ipaddress, sampler1_port)
    sampler3_osc = udp_client.SimpleUDPClient(sampler_ipaddress, sampler3_port)
    
    # start maskers
    msg_address = f'/{source1_name}/{1}/add'
    msg_contents = [1, 1]  # loop_count, linear_gain
    # print(msg_address)
    sampler1_osc.send_message(msg_address, msg_contents)
    
    time.sleep(2)
    
    # start maskers
    msg_address = f'/{source3_name}/{1}/add'
    msg_contents = [1, 1]  # loop_count, linear_gain
    # print(msg_address)
    sampler3_osc.send_message(msg_address, msg_contents)
    
    time.sleep(4)   
    
    tascar_cli.stop()
    