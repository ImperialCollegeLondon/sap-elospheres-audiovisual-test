import subprocess
from pathlib import Path

module_path=Path(__file__).parent.absolute()
# TODO: Add platform check/alternatives
# TODO: Modify ps1 scripts so that they return success values
# TODO: Make the whole thing self checking
START_LOCAL_SCRIPT=Path(module_path,"start_local.ps1")
START_REMOTE_SCRIPT=Path(module_path,"start_wsl.ps1")
TEST_REMOTE_METRONOME_SCRIPT=Path(module_path,"test_metronome.ps1")

class JackTripControl:
    # TODO: add state checks for jack and jacktrip processes on local and remote
    def __init__(self):
        self.isRunning = False;


    def start(self):
        # start remote scrip first because we it saves its IP address to a file
        # that is read by the local script
        subprocess.run(["powershell.exe",START_REMOTE_SCRIPT], shell=True, check=True)
        subprocess.run(["powershell.exe",START_LOCAL_SCRIPT], shell=True, check=True)
        self.isRunning = True

    def stop(self):
        if self.isRunning:
            pass #TODO kill the processes

    def testMetronomeManual(self):
        subprocess.run(["powershell.exe",TEST_REMOTE_METRONOME_SCRIPT], check=True)