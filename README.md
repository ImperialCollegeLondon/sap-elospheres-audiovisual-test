# ELO-SPHERES Audiovisual Test (SEAT)

Implements the logic for running audiovisual intelligibility tests.

Targets Windows platform with Windows Subsystem for Linux already installed.

## Installation
1. Open an anaconda shell

    See https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html for installation instructions.

1. Get the code and test data using
    ```
    (base) git clone https://github.com/ImperialCollegeLondon/sap-elospheres-audiovisual-test.git C:\gitwin\ImperialCollegeLondon\sap-elospheres-audiovisual-test
    ```
    N.B. For now, the built-in tests have files with hardcoded paths. This is pretty ugly but avoids lots of complexity.

1. Create a new conda environment
    ```
    (base) conda env create -n seat --file seat.yml
    ```
    N.B. You can call the environment (-n \<env_name\>) whatever you like but `seat` will be used here.

1. Activate the new environment and change into the main seat directory
    ```
    (base) conda activate seat
    (seat) cd seat
    ```

## Test the installation
These are just to check that everything installed properly. They are by no means exhaustive.

### Unit tests
These all run in one go and don't require any user interaction
```
(seat) python -m unittest discover unit_tests
```

### Manual tests
These test basic functionality and require user interaction.

Check the gui system is working. A window should pop up. No specific values need to be entered. Press cancel or close the window to move onto the finish the test.
```
(seat) python -m manual_tests.test_pysimplegui
```

Check the audio system is working. Four console windows will pop up. Identify the two that relate to JackTrip - one each for the local (Windows) and remote (WSL) sides. Once the connection is established return to the original anaconda console and press Enter to start a metronome and again to stop it.
```
(seat) python -m manual_tests.test_jacktrip_audio
```

### Demo tests
These demonstrate the functionality of a perceptual test.

Close any open consoles from previous tests and open a new anaconda prompt

Setup the environment
```
(base) conda activate seat
(seat) python .\setup_jacktrip_wsl.py
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
