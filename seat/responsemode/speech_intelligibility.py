from .response_mode import ResponseMode
import numpy as np
import pandas
import PySimpleGUI as sg
import util
import pathlib


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

        # grab the bits we need
        self.data_root_dir = config["root_dir"]
        keywords_file = config["keyword_file"]
        keywords_file_path = pathlib.Path(self.data_root_dir, keywords_file)
        util.check_path_is_file(keywords_file_path)
        self.keywords_df = pandas.read_csv(keywords_file_path, header=None)
        # print(self.keywords_df)

    def show_prompt(self, stimulus_id):
        # keywords = ['Word 1', 'Word 2', 'Word 3', 'Word 4', 'Word 5']
        # print(stimulus_id)
        keywords = self.keywords_df.loc[stimulus_id, :]
        # print(keywords)
        button_row_layout = []
        self.button_keys = []
        self.kw_correct = {}
        for kw_num, keyword in enumerate(keywords):
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
                return result
            elif event in self.button_keys:
                self.kw_correct[event] = not self.kw_correct[event]
                self.window.Element(event).Update(
                    button_color=(('white', ('red', 'green')[self.kw_correct[event]])))
            # print(self.kw_correct)
        # self.window.Hide()
