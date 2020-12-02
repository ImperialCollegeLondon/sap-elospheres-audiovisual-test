import pathlib
import responsemode

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "02_TargetSpeechTwoMaskers")
    config = {
                "root_dir": data_root_dir,
                "keyword_file": "keywords.txt"
            }
    response_mode = responsemode.ExperimenterSelectsCorrectKeywords(config)

    response_mode.show_prompt(0)
    response_mode.wait()
