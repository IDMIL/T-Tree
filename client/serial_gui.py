# Standard libraries
import json
import threading
from time import sleep

# Third-party libraries
import PySimpleGUI as sg
import serial
import serial.tools.list_ports

DEFAULT_DEVICE = '/dev/ttyUSB0'
ser = serial.Serial(DEFAULT_DEVICE, baudrate=115200)

recv_message_box = sg.Multiline(autoscroll=True, auto_refresh=True, disabled=True, size=(80,10))
send_message_box = sg.Combo(('sendsettings', 'endsettings', 'getstrsetting', 'sendconfig', 'endconfig', 'reboot'), readonly=True)
ports_dropdown = sg.Combo((), readonly=True, size=(20, 5))

def window_function():
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Ports'), ports_dropdown, sg.Button('Refresh')],
                [sg.Text('Received messages')],
                [sg.Button('Open')],
                [recv_message_box],
                [sg.Text('Send message:'), send_message_box, sg.Button('Send')],
                [sg.Button('Settings'), sg.Button('Config')],
                [sg.Button('Quit')],
    ]
    # Create the Window
    window = sg.Window('Serial Communicator', layout)
    while True:
        event, values = window.read() 
        if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
            break
        elif event == 'Send':
            message = send_message_box.get()
            ser.write(bytes(message, 'utf-8'))
            print(f'sending {message}')
        elif event == 'Refresh':
            ports = serial.tools.list_ports.comports()
            ports_dropdown.update([port for (port, desc, hwid) in ports])
        elif event == 'Settings':
            ser.write(bytes(read_json('settings.json'), 'utf-8'))
        elif event == 'Config':
            ser.write(bytes(read_json('config.json'), 'utf-8'))
    window.close()

def read_json(filename):
    with open(filename) as f:
        return json.dumps(json.loads(f.read()))

def serial_daemon():
    while True:
        data = ser.readline().decode('utf-8', 'backslashreplace')
        recv_message_box.print(data)


def main():
    w = threading.Thread(target=window_function)
    w.start()
    x = threading.Thread(target=serial_daemon)
    x.start()


if __name__ == '__main__':
    main()