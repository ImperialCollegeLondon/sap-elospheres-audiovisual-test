# ELO-SPHERES Audiovisual Test (SEAT)

Implements the logic for running audiovisual intelligibility tests.

Targets Windows platform with Windows Subsystem for Linux already installed.

## Pre-requisites
- Ubuntu installed under WSL2
- 

## Installation

There are two main ways to install the development requirements: using `pip` or Anaconda

### With `pip`

1. Clone this repository
1. Create a virtual environment with python 3.8 or higher:
    ```
    python -m venv .venv
    ```

1. Activate it:
    ```
    # In terminal (MacOS and Linux)
    $ source .venv/bin/activate
    ```
    ```
    # In cmd.exe
    venv\Scripts\activate.bat
    # In PowerShell
    venv\Scripts\Activate.ps1
    ```

1. Install development requirements in the virtual environment:
    ```
    pip install -r dev-requirements.txt
    ```

### With Anaconda

1. Open an anaconda shell

    See https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html for installation instructions.

1. Get the code and test data using
    ```
    (base) git clone https://github.com/ImperialCollegeLondon/sap-elospheres-audiovisual-test.git C:\gitwin\ImperialCollegeLondon\sap-elospheres-audiovisual-test
    ```
    N.B. For now, the built-in tests have files with hardcoded paths. This is pretty ugly but avoids lots of complexity.

1. Create a new conda environment
    ```
    (base) conda create python=3.8.3 -n seat
    ```
    N.B. You can call the environment (-n \<env_name\>) whatever you like but `seat` will be used here.

2. Activate the new environment, install the requirements and change into the main `seat` directory
    ```
    (base) conda activate seat
    (seat) conda install -c conda-forge --file dev-requirements.txt
    (seat) cd seat
    ```

## Test the installation
These are just to check that everything installed properly. They are by no means exhaustive.

### Unit tests
These all run in one go and don't require any user interaction
```
(seat) python -m unittest discover unit_tests
```

## Setup audio
Run
```
(seat) python .\setup_jacktrip_wsl.py
```
Switch to the 'settings' tab and ensure appropriate values have been entered.
Once satisfied, click the Start button. Switch to the console tab to inspect the
output. The status at the bottom of the gui will change from Disconnected to
Starting. Once the connection is established it will show 'Connected'

Press the Test button to play a metronome test tone on the left channel. Note
that the metronome is a jack-enabled executable running under WSL. Press again
to stop the test.

Assuming everything is ok, press the Stop button, return to the settings tab and
press Save. These settings will be used by default from now on.


### Demo tests
These demonstrate the functionality of a perceptual test.

Close any open consoles from previous tests and open a new anaconda prompt

Setup the environment
```
(base) conda activate seat
(seat) python .\start_jacktrip_wsl.py
```
Note that in this case jacktrip is left running. Once you have finished you can
end jacktrip using
```
(seat) python .\stop_jacktrip_wsl.py
```


The first test demonstrates a signal detection task
```
(seat) python -m demo_tests.test_01_targettoneinnoise
```

The second test demonstrates a speech intelligibility task
```
python -m demo_tests.test_02_targetspeechtwomaskers
```
If the listeningeffortplayer app is running then the target speech video should be visible.


## Real usage

- Open the ListeningEffortPlayer app
- Open anaconda prompt
  - Activate the `seat` environment
  - Run gui.py
  - Choose the csv file which contains all the block definitions
  - Select the block to run and add optional subject metadata
  - Click 'Run' to start the block
  - Experimenter selects the correctly reported keywords

```
cd C:\gitwin\ImperialCollegeLondon\sap-elospheres-audiovisual-test
git pull
conda env update -n seat --file seat.yml
conda activate seat
cd seat
python .\gui.py
#
# In the background jacktripcontrol will start with the previously saved settings
# Once the 'jtc...' button turns green and you have selected a block you can press 'Run'
# press the 'jtc...' button to change the settings and/or restart jacktrip.
```

### Managing Dependencies
Dependencies are managed using the [`pip-tools`] tool chain. Unpinned dependencies are specified in `pyproject.toml`. Pinned versions are then produced with: `pip-compile`.

To add/remove packages, edit `pyproject.toml` and run the above command. To upgrade all existing dependencies run: `pip-compile --upgrade`.

Dependencies for developers are listed separately as optional, with the pinned versions being saved to `dev-requirements.txt` instead. `pip-tools` can also manage these dependencies by adding extra arguments, e.g.: `pip-compile --extra dev -o dev-requirements.txt`.

When dependencies are upgraded, both `requirements.txt` and `dev-requirements.txt` should be regenerated so that they are compatible with each other and then synced with your virtual environment with: `pip-sync dev-requirements.txt requirements.txt`.

Versions can be restricted from updating within the `pyproject.toml` using standard python package version specifiers, i.e. `"black<23"` or `"pip-tools!=6.12.2"`.

[`pip-tools`]: https://pip-tools.readthedocs.io/en/latest/


<!--
Deprecated
### Manual tests
These test basic functionality and require user interaction.

Check the gui system is working. A window should pop up. No specific values need to be entered. Press cancel or close the window to move onto the finish the test.
```
(seat) python -m manual_tests.test_pysimplegui
```

Check the audio system is working. Prompts will guide you. A GUI will be shown where settings can be adjusted, if required. Four console windows show the output of
the jack/jacktrip processes. Once everything is running a metronome is used to test the audio works.
```
(seat) python -m manual_tests.test_jacktrip_audio
```
-->
