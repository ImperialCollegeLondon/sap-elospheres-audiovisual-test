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

    # remove the idle video
    for screen_id in range(1,4):
        video_client.send_message("/video/set_idle", [screen_id, ''])
    
    
    # Try positioning videos in the screens
    parent_directory = pathlib.PureWindowsPath(pathlib.Path(
                        'C:\\','gitwin','ImperialCollegeLondon','sap-elospheres-audiovisual-test','seat'))
    video_path = pathlib.Path.joinpath(parent_directory, "demo_data", "02_TargetSpeechTwoMaskers", "target",
        "01_ieee01s01.mp4")
          
    for screen_id in range(1,4):
        video_client.send_message("/video/play", [screen_id, str(video_path)])
        
    