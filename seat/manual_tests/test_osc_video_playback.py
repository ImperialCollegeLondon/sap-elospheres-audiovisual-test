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

    # set the camera rig rotation so that front direction is correct
    # EulerX, EulerY, EulerZ in Unity's left handed, z is depth coordinates
    # video_client.send_message("/set_orientation", [0., 90., 0.])

    screen_id = 0 # skybox
    # video_path = pathlib.Path('C:\Users\alastair\Dropbox\ELOSPHERES\data\20220404_R909_measurements\360_videos_v2\1.5 m\±45.mp4')
    # video_client.send_message("/video/play", [screen_id, str(video_path)])
    
    video_path = pathlib.PureWindowsPath(
                        pathlib.Path('C:\\','Users','alastair','Dropbox','ELOSPHERES','data',
                                     '20220404_R909_measurements','360_videos_v3','1.0 m','45.mp4'))
    video_path = pathlib.PureWindowsPath(
                     pathlib.Path('C:\\','Users','alastair','Dropbox','ELOSPHERES','data',
                                  '20220404_R909_measurements','360_videos_v4','1.0 m','45.mp4'))
    # print(f'{video_path}')
#     print(f'{str(video_path)}')
    video_client.send_message("/video/play", [screen_id, str(video_path)]) 

    # Try positioning videos in the screens
    parent_directory = pathlib.PureWindowsPath(pathlib.Path(
                        'C:\\','gitwin','ImperialCollegeLondon','sap-elospheres-audiovisual-test','seat'))
    video_path = pathlib.Path.joinpath(parent_directory, "demo_data", "02_TargetSpeechTwoMaskers", "target",
        "01_ieee01s01.mp4")
    

    # start an idle video, so that it loops indefinitely
    for screen_id in range(1,4):
        video_client.send_message("/video/set_idle", [screen_id, str(video_path)])
        video_client.send_message("/video/start_idle", [screen_id])

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
    # video_client.send_message("/video/position",[
 #        screen_id,
 #        0., 89., 0.,
 #        0., 0.,
 #        167., 97.])