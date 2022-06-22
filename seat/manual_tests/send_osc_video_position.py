import pathlib
from pythonosc import udp_client
import numpy as np
import time


if __name__ == '__main__':
    # this_directory = pathlib.Path(__file__).parent.absolute()
#     parent_directory = this_directory.parent
#     video_path = pathlib.Path(
#         parent_directory, "demo_data", "02_TargetSpeechTwoMaskers", "target",
#         "01_ieee01s01.mp4")
    # tmp_dir = pathlib.Path(parent_directory,
    #                        "local_unversioned_tmp_files",
    #                        datetime.now().strftime("%Y%m%d_%H%M%S"))
    # tmp_dir.mkdir(parents=True, exist_ok=True)
    # config = {
    #     "keywords_path": str(pathlib.Path(data_root_dir, "keywords.txt")),
    #     "log_path": str(pathlib.Path(tmp_dir, 'response_log.csv'))
    # }
    
    # setup the client
    ipaddress = '127.0.0.1'
    ipaddress = '192.168.1.100'
    oscport = 7000
    video_client = udp_client.SimpleUDPClient(ipaddress, oscport)

        # position the screen
    # 		{
    # 			(typeof(int), "Video player ID (1-3)"),
    # 			(typeof(float), "Azimuth (degrees)"),
    # 			(typeof(float), "Inclination (degrees)"),
    # 			(typeof(float), "Twist (degrees)"),
    # 			(typeof(float), "Rotation around X axis (degrees)"),
    # 			(typeof(float), "Rotation around Y axis (degrees)"),
    # 			(typeof(float), "Width (scale)"),
    # 			(typeof(float), "Height (scale)"),
    # 		}
    scale_factor  = 1.1
    
    screen_id = 1    
    video_client.send_message("/video/position",[
        screen_id,
        0., -45.5, 0.5,
        0., 0.,
        scale_factor * 167., scale_factor *97.])
    
    screen_id = 2    
    video_client.send_message("/video/position",[
        screen_id,
        0., -1., -1.3,
        0., 0.,
        scale_factor * 167., scale_factor *97.])
        
    screen_id = 3
    video_client.send_message("/video/position",[
        screen_id,
        0., 44.5, -1.5,
        0., 0.,
        scale_factor * 167., scale_factor *97.])