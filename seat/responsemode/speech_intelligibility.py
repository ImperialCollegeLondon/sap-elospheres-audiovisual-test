from .response_mode import ResponseMode
import numpy as np
import pandas
import PySimpleGUI as sg
import util
import pathlib
import pprint

def kw_button(text, key):
    return sg.B(text,
                size=(10, 1),
                button_color=('white', 'red'),
                key=key)


class ExperimenterSelectsCorrectKeywords(ResponseMode):
    """
    A window is created and populated with buttons. The experimenter clicks on
    the buttons corresponding to the correctly identified keywords.
    """
    def __init__(self, config):
        # pprint.pprint(config)

        # grab the bits we need
        keywords_path = pathlib.Path(config["keywords_path"])
        util.check_path_is_file(keywords_path)
        self.keywords_df = pandas.read_csv(keywords_path, header=None)
        # print(self.keywords_df)

        self.write_to_log = False
        if "log_path" in config:
            print(config["log_path"])
            self.write_to_log = True
            self.log_path = pathlib.Path(config["log_path"])
            self.log_path.touch(exist_ok=False)  # do NOT overwrite!

    def show_prompt(self, stimulus_id):
        # keywords = ['Word 1', 'Word 2', 'Word 3', 'Word 4', 'Word 5']
        # print(stimulus_id)
        self.keywords = self.keywords_df.loc[stimulus_id, :]
        self.stimulus_id = stimulus_id
        # print(self.keywords)
        button_row_layout = []
        self.button_keys = []
        self.kw_correct = {}
        for kw_num, keyword in enumerate(self.keywords):
            button_key = 'kw_' + str(kw_num)
            button_row_layout += [kw_button(keyword, key=button_key)]
            self.button_keys += [button_key]
            self.kw_correct[button_key] = False
        # print(self.button_keys)

        self.done_button_key = 'done_button'
        layout = [[sg.Text('Select the correctly identified words')],
                  button_row_layout,
                  [sg.Button('Done', key=self.done_button_key)]
                  ]

        self.window = sg.Window('Speech intelligibility - keywords', layout,
                                keep_on_top=True,
                                finalize=True)

    def wait(self):
        while True:             # Event Loop
            event, values = self.window.Read()
            # print(event, values)
            if event == sg.WIN_CLOSED:
                self.window.close()
                return
            elif event == self.done_button_key:
                # convert output to an array
                result = []
                for i in range(len(self.button_keys)):
                    result.append(self.kw_correct[self.button_keys[i]])
                # print(result)

                if self.write_to_log:
                    df_to_write = pandas.concat(
                        [pandas.DataFrame([self.stimulus_id]),
                         self.keywords,
                         pandas.DataFrame(result)]
                        )
                    df_to_write.T.to_csv(self.log_path,
                                         index=False,
                                         header=False,
                                         mode='a')
                self.window.close()
                return result
            elif event in self.button_keys:
                self.kw_correct[event] = not self.kw_correct[event]
                self.window.Element(event).Update(
                    button_color=(('white', ('red', 'green')[self.kw_correct[event]])))
            # print(self.kw_correct)
