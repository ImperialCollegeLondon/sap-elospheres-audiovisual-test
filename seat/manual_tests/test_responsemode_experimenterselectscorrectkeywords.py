import pathlib
import responsemode
from datetime import datetime

if __name__ == '__main__':
    this_directory = pathlib.Path(__file__).parent.absolute()
    parent_directory = this_directory.parent
    data_root_dir = pathlib.Path(
        parent_directory, "demo_data", "02_TargetSpeechTwoMaskers")
    tmp_dir = pathlib.Path(parent_directory,
                           "local_unversioned_tmp_files",
                           datetime.now().strftime("%Y%m%d_%H%M%S"))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "keywords_path": str(pathlib.Path(data_root_dir, "keywords.txt")),
        "log_path": str(pathlib.Path(tmp_dir, 'response_log.csv'))
    }
    response_mode = responsemode.ExperimenterSelectsCorrectKeywords(config)

    response_mode.show_prompt(0)
    response_mode.wait()

    response_mode.show_prompt(2)
    response_mode.wait()
