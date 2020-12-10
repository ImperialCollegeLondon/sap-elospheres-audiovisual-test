from .response_mode import ResponseMode
import PySimpleGUI as sg


def kw_button(text, key):
    return sg.B(text,
                size=(10, 1),
                button_color=('white', 'red'),
                key=key)


class BinaryChoice(ResponseMode):
    """
    A window is created and populated with two buttons: Yes/No.
    """
    def __init__(self, config):

        # grab the bits we need
        self.ground_truth = config["signal_present"]

    def show_prompt(self, stimulus_id):
        self.ground_truth_this_stimulus = self.ground_truth[stimulus_id]
        self.no_key = '_NO_'
        self.yes_key = '_YES_'
        layout = [[sg.Text('Was there a signal present?')],
                  [sg.Button('No', key=self.no_key,
                             button_color=('white', 'red')),
                   sg.Button('Yes', key=self.yes_key,
                             button_color=('white', 'green'))]
                  ]

        self.window = sg.Window('Binary choice', layout,
                                keep_on_top=True,
                                finalize=True)

    def wait(self):
        while True:             # Event Loop
            event, values = self.window.Read()
            # print(event, values)
            if event == sg.WIN_CLOSED:
                self.window.close()
                return
            elif event == self.no_key:
                response = False
                break
            elif event == self.yes_key:
                response = True
                break
        result = (response == self.ground_truth_this_stimulus)
        # print(result)
        self.window.close()
        return result
