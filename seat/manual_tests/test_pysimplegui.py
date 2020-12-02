import PySimpleGUI as sg

# test 1
if False:
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Text('Some text on Row 1')],
              [sg.Text('Enter something on Row 2'), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        # if user closes window or clicks cancel
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        print('You entered ', values[0])

    window.close()

# test 2
if False:
    sg.theme('BluePurple')

    layout = [[sg.Text('Your typed chars appear here:'),
               sg.Text(size=(15, 1), key='-OUTPUT-')],
              [sg.Input(key='-IN-')],
              [sg.Button('Show'), sg.Button('Exit')]]

    window = sg.Window('Pattern 2B', layout)

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Show':
            # Update the "output" text element to be the value of "input" element
            window['-OUTPUT-'].update(values['-IN-'])

    window.close()


# test 3 - toggle Button
def kwB(text, key):
    return sg.B(text,
                size=(10, 1),
                button_color=('white', 'red'),
                key=key)


if True:
    print(('False val', 'True val')[True])
    keywords = ['Word 1', 'Word 2', 'Word 3', 'Word 4', 'Word 5']
    button_row_layout = []
    button_keys = []
    keyword_was_identified = {}
    for kw_num, keyword in enumerate(keywords):
        button_key = 'kw_' + str(kw_num)
        button_row_layout += [kwB(keyword, key=button_key)]
        button_keys += [button_key]
        keyword_was_identified[button_key] = False

    print(button_keys)

    layout = [[sg.Text('Select the correctly identified words')],
              button_row_layout,
              [sg.Button('Exit')]
              ]

    window = sg.Window('Toggle Button Example', layout)

    down = True
    graphic_off = True
    while True:             # Event Loop
        event, values = window.Read()
        print(event, values)
        if event in (None, 'Exit'):
            # convert output to an array
            result = []
            for i in range(len(button_keys)):
                result.append(keyword_was_identified[button_keys[i]])
            print(result)
            break
        elif event in button_keys:                # if the normal button that changes color and text
            keyword_was_identified[event] = not keyword_was_identified[event]
            # window.Element(event).Update(('Off', 'On')[keyword_was_identified[event]],
            #                              button_color=(('white', ('red', 'green')[keyword_was_identified[event]])))
            window.Element(event).Update(button_color=(('white', ('red', 'green')[keyword_was_identified[event]])))
        print(keyword_was_identified)
    window.Close()
