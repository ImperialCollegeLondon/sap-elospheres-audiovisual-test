# Manual tests

The scripts in this module are designed to test certain functionality that requires human interaction or verification.  Some of them were created as proof-of-concept scripts which are more-or-less independent of the main `seat` code.  In other cases, a small part or subset of parts are being tested.

It is possible that some tests may be deprecated as the code base develops.



### `test_tascar_cli_on_mac.py`

```
python -m manual_tests.test_tascar_cli_on_mac
```
Launches tascar, runs a scene for 5 seconds then stops it.  The scene renders a moving pink noise source using the `hrtf` receiver type.


### `test_tascar_cli_on_mac_with_osc.py`

```
python -m manual_tests.test_tascar_cli_on_mac_with_osc
```
Launches tascar, runs a scene for several seconds then stops it.  The scene renders a moving pink noise source using the `hrtf` receiver type.  A sequence of OSC commands alternately mute/unmute the source.

### `test_tascar_cli_on_mac_with_osc_samplers.py`

```
python -m manual_tests.test_tascar_cli_on_mac_with_osc_samplers
```
Launches tascar, starts scene with noise source to the rear. Sends OSC commands to trigger samplers.