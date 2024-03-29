import pathlib
from pythonosc import udp_client
import numpy as np
import time


if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    video_path = pathlib.Path(
        parent_directory, "demo_data", "02_TargetSpeechTwoMaskers", "target",
        "01_ieee01s01.mp4")
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
    oscport = 7000
    video_client = udp_client.SimpleUDPClient(ipaddress, oscport)

    # set the camera rig rotation so that front direction is correct
    # EulerX, EulerY, EulerZ in Unity's left handed, z is depth coordinates
    # video_client.send_message("/set_orientation", [0., 90., 0.])

    screen_id = 2

    # start an idle video, so that it loops indefinitely
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
    video_client.send_message("/video/position",[
        screen_id,
        0., 0., 0.,
        0., 0.,
        167., 97.])
    
    
    for az_deg in np.arange(0., 360., 10):
        video_client.send_message("/video/position",[
            screen_id,
            0., az_deg, 0., 
            0., 0.,
            167., 97.])
        
        time.sleep(0.1)
        
    # final positions
    video_client.send_message("/video/position",[1,
        0., -45., 0., 0., 0., 167., 97.])   
    video_client.send_message("/video/position",[2,
        0., 0., 0., 0., 0., 167., 97.])
    video_client.send_message("/video/position",[3,
        0., 45., 0., 0., 0., 167., 97.])