from pathlib import Path
import psutil
import subprocess
import time


module_path = Path(__file__).parent.absolute()
# TODO: Add platform check/alternatives
# TODO: Modify ps1 scripts so that they return success values
# TODO: Make the whole thing self checking
INIT_SCRIPT = Path(module_path, "init_env.ps1")
START_LOCAL_SCRIPT = Path(module_path, "start_local.ps1")
START_REMOTE_SCRIPT = Path(module_path, "start_wsl.ps1")
KILL_REMOTE_SCRIPT = Path(module_path, "kill_wsl.ps1")
TEST_REMOTE_METRONOME_SCRIPT = Path(module_path, "test_metronome.ps1")
CONNECT_SOUNDCARD_SCRIPT = Path(module_path,
                                "connect_jacktrip_receive_to_soundcard.ps1")
DISCONNECT_SOUNDCARD_SCRIPT = Path(module_path,
                                   "disconnect_jacktrip_receive_from_soundcard.ps1")


class JackTripControl:
    """
    Python interface which wraps scripts to start (TODO: and stop) the jack and
    jacktrip processes
    """
    # TODO: add state checks for jack and jacktrip processes on local and
    # remote
    def __init__(self):
        self.isRunning = False

    def start(self):
        # start remote scrip first because we it saves its IP address to a file
        # that is read by the local script
        subprocess.run(["powershell.exe", INIT_SCRIPT], shell=True,
                       check=True)
        subprocess.run(["powershell.exe", START_REMOTE_SCRIPT], shell=True,
                       check=True)
        subprocess.run(["powershell.exe", START_LOCAL_SCRIPT], shell=True,
                       check=True)
        self.isRunning = True

    def stop(self):
        # this check fails if we want to start/stop from
        # separate scripts
        #if self.isRunning: 
            subprocess.run(["powershell.exe", KILL_REMOTE_SCRIPT],
                           shell=True,check=True)
            
            
            local_process_names = ["jackd.exe"] #only need to kill jack (jacktrip will die anyway)

            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.name() in local_process_names:
                    proc.terminate()

            

            time.sleep(1)
            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.name() in local_process_names:
                    proc.kill()
            self.isRunning = False

    def connect(self):
        if self.isRunning:
            subprocess.run(["powershell.exe", CONNECT_SOUNDCARD_SCRIPT],
                           check=True)
        else:
            print("need to start before connecting")

    def disconnect(self):
        subprocess.run(["powershell.exe", DISCONNECT_SOUNDCARD_SCRIPT],
                       check=True)

    def test_metronome_manual(self):
        subprocess.run(["powershell.exe", TEST_REMOTE_METRONOME_SCRIPT],
                       check=True)


if __name__ == '__main__':
    jtc = JackTripControl()
    jtc.start()
