import PySimpleGUI as sg

sg.theme('DarkAmber')
layout = [
        [sg.Text("EasyCSS")],
        [sg.Text("Button class name"), sg.InputText()],
        [sg.Button("Save")]
        ]

window = sg.Window("EasyCSS", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    print('The button class name is: ' + values[0])

window.close()
