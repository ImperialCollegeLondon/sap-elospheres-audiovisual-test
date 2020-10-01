# import av_renderer_control
from .av_renderer_control import AVRendererControl
import confuse
import pathlib
import pandas as pd
import pprint

# helper functions
# leading underscore avoids being imported
def _is_valid_ipaddress(addressToTest):
    try:
        parsedAddress = ipaddress.ip_address(addressToTest)
        print('parsedAddress:' + str(parsedAddress))
        return True
    except ValueError as err:
        print(err)
        print('Invalid address:', addressToTest)
        return False


class ListeningEffortPlayerAndTascarUsingOSCBase(AVRendererControl):
    """
    Base class to implement core functionality of co-ordinating the unity-based
    visual display with headtracking data sent via osc to tascar-based audio
    renderer running on windows subsytem for linux
    """
    def __init__(self):
        # get the IP addresses
        appName='ListeningEffortPlayerAndTascarUsingOSC'
        self.moduleConfig = confuse.Configuration(appName, __name__)

    # implement conext manager magic
    def __enter__(self):
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        self.close_osc()

    def setup_osc(self):
        # get the tascar ip address
        # if specified in the config use it, otherwise look in enviornment variable
        tascar_ipaddress = self.moduleConfig['tascar']['ipaddress'].get(str)
        print('config tascar.ipaddress:' + tascar_ipaddress)
        if not _is_valid_ipaddress(tascar_ipaddress):
            variablename=self.moduleConfig['tascar']['ipenvvariable'].get(str)
            filename=os.environ.get(variablename)
            with open(filename, "r") as myfile:
                tascar_ipaddress = myfile.readline().strip()
            print('env {}: {}'.format(variablename, tascar_ipaddress))
            if not _is_valid_ipaddress(tascar_ipaddress):
                # failed to get a valid ipaddress
                print(tascar_ipaddress)
                raise ValueError
            # store it in config in case we need it again
            self.moduleConfig['tascar']['ipaddress']=tascar_ipaddress

        # TODO: check validity of all ip addresses
        # open the OSC comms
        self.video_client = udp_client.SimpleUDPClient(
            self.moduleConfig['unity']['ipaddress'].get(str),
            self.moduleConfig['unity']['oscport'].get(int))
        self.tascar_client = udp_client.SimpleUDPClient(
            self.moduleConfig['tascar']['ipaddress'].get(str),
            self.moduleConfig['tascar']['oscport'].get(int))
        self.sampler_client1 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source1']['oscport'].get(int))
        self.sampler_client2 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source2']['oscport'].get(int))
        self.sampler_client3 = udp_client.SimpleUDPClient(
            self.moduleConfig['sampler']['ipaddress'].get(str),
            self.moduleConfig['sampler']['source3']['oscport'].get(int))

        # tell unity where to send the head rotation data
        self.video_client.send_message("/set_client_address",
            [self.moduleConfig['tascar']['ipaddress'].get(str),
             self.moduleConfig['tascar']['oscport'].get(int)])

    def close_osc(self):
        # this isn't really necessary but avoids warnings in unittest
        if hasattr(self, 'video_client'):
            self.video_client._sock.close()
        if hasattr(self, 'tascar_client'):
            self.tascar_client._sock.close()
        if hasattr(self, 'sampler_client1'):
            self.sampler_client1._sock.close()
        if hasattr(self, 'sampler_client2'):
            self.sampler_client2._sock.close()
        if hasattr(self, 'sampler_client3'):
            self.sampler_client3._sock.close()


class TargetToneInNoise(ListeningEffortPlayerAndTascarUsingOSCBase):
    """
    Demo to show probe level control without requiring speech files
    """

    # Override constructor to get the right config settings
    def __init__(self):
        # get the IP addresses
        app_name='TargetToneInNoise'
        self.moduleConfig = confuse.Configuration(app_name, __name__)

    def load_config(self,config):
        # grab the bits we need
        # - blocks are presented in order
        # current_block_index=config["state_control"]["current_block_index"].get(int)
        # print('current_block_index: '+str(current_block_index))
        # block_config = config["blocks"][current_block_index]

        block_config = config["blocks"][config["state_control"]["current_block_index"].get(int)]
        print('Block:')
        print('\tid: '+block_config["id"].get(str))
        print('\tlistening_condition_id: '+block_config["listening_condition_id"].get(str))


        # - pandas dataframe makes it easy to find the right listening condition
        pprint.pprint(config["listening_conditions"].get())
        df = pd.DataFrame(config["listening_conditions"].get()) # dataframe from list of dicts
        pprint.pprint(df)
        matching_index = df[df["id"] == block_config["listening_condition_id"].get(str)].index.values
        num_of_matches = len(matching_index)
        # print('Looking for listening_conditions.id: ',block_config["listening_condition_id"].get(str))
        # lc_df = df[ (df["id"] == block_config["listening_condition_id"].get(str))]
        # num_of_matches = len(lc_df)
        assert num_of_matches==1, "expected one match but got {}".format(num_of_matches)
        lc_config = config["listening_conditions"][matching_index[0]]

        # get the fully qualified path to the skybox video in stages
        skybox_dir = self.skybox=pathlib.Path(config["paths"]["unity_data"]["root_dir"].get(str),
            config["paths"]["unity_data"]["skybox_rel_dir"].get(str))
        skybox_filename = lc_config["avrenderer"]["skybox_file"].get(str)
        self.skybox_absolute_path = pathlib.Path(skybox_dir,skybox_filename)

    def setup(self):
        pass

    def start_scene(self):
        pass

    def set_probe_level(self,probeLevel):
        pass

    def present_next_trial(self):
        pass
