# Standard libraries
import threading
from time import sleep

# Third-party libraries
import PySimpleGUI as sg

sg.theme('DarkAmber')   # Add a touch of color
message_box = sg.Multiline(autoscroll=True, auto_refresh=True, disabled=True, size=(80,10))
# All the stuff inside your window.
layout = [  [sg.Text('Received messages')],
            [message_box],
            [sg.Text('Send message:'), sg.InputText(), sg.Button('Send', key='send_btn')],
]

def window_function():
    # Create the Window
    window = sg.Window('Serial Communicator', layout)
    while True:
        event, values = window.read() 
        print(event, values)   
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        print('You entered ', values[0])

    window.close()

w = threading.Thread(target=window_function)
w.start()

sleep(2)
message_box.print('hello')

sleep(1)
message_box.print('world')