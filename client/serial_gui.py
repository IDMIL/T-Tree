# Standard libraries
import threading
from time import sleep

# Third-party libraries
import PySimpleGUI as sg

def window_function():
    sg.theme('DarkAmber')   # Add a touch of color
    recv_message_box = sg.Multiline(autoscroll=True, auto_refresh=True, disabled=True, size=(80,10))
    send_message_box = sg.InputText()
    # All the stuff inside your window.
    layout = [  [sg.Text('Received messages')],
                [recv_message_box],
                [sg.Text('Send message:'), send_message_box, sg.Button('Send')],
                [sg.Button('Quit')],
    ]
    # Create the Window
    window = sg.Window('Serial Communicator', layout)
    while True:
        event, values = window.read() 
        if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
            break
        elif event == 'Send':
            print('You entered', send_message_box.get())

    window.close()


def main():
    w = threading.Thread(target=window_function)
    w.start()


if __name__ == '__main__':
    main()