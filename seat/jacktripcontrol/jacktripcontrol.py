import subprocess
from pathlib import Path

module_path=Path(__file__).parent.absolute()
# TODO: Add platform check/alternatives
# TODO: Modify ps1 scripts so that they return success values
# TODO: Make the whole thing self checking
START_LOCAL_SCRIPT=Path(module_path,"start_local.ps1")
START_REMOTE_SCRIPT=Path(module_path,"start_wsl.ps1")
TEST_REMOTE_METRONOME_SCRIPT=Path(module_path,"test_metronome.ps1")

def start():
    subprocess.run(["powershell.exe",START_LOCAL_SCRIPT], shell=True, check=True)
    subprocess.run(["powershell.exe",START_REMOTE_SCRIPT], shell=True, check=True)

def testMetronomeManual():
    subprocess.run(["powershell.exe",TEST_REMOTE_METRONOME_SCRIPT], check=True)


def stop():
    # TODO: implement killing of all the processes
    pass

if __name__ == '__main__':
    start()
    testMetronomeManual()
