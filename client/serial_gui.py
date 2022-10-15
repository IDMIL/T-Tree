# Standard libraries
import json
import threading
from time import sleep

# Third-party libraries
import PySimpleGUI as sg
import serial
import serial.tools.list_ports

DEFAULT_DEVICE = '/dev/ttyUSB1'
ser = serial.Serial()
ser.baudrate = 115200

recv_message_box = sg.Multiline(autoscroll=False, auto_refresh=True, disabled=True, size=(80,10), expand_y=True, expand_x=True)
send_message_box = sg.Combo(['reboot', 'whatareyou', 'readconfig', 'writeconfig', 'readsettings', 'writesettings'], size=(20, 5))
ports_dropdown = sg.Combo((), readonly=True, size=(20, 5))
settings_button = sg.Button('Settings', disabled=True)
config_button = sg.Button('Config', disabled=True)
send_button = sg.Button('Send', disabled=True)
buttons = [settings_button, config_button, send_button]
open_port = sg.Text('')

def window_function():
    # sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [
        [sg.Text('Ports'), ports_dropdown, sg.Button('Refresh')],
        [sg.Button('Open'), open_port],
        [sg.Text('Received messages')],
        [recv_message_box],
        [sg.Text('Send message:'), send_message_box, send_button],
        [settings_button, config_button],
        [sg.Button('Quit')],
    ]
    config_layout = [
        [sg.Text("Device Name"), sg.Input(key='device', readonly=True)],
        [sg.Text("Device ID"), sg.Input(key='id', readonly=True)],
        [sg.Text("Device Author"), sg.Input(key='author', readonly=True)],
        [sg.Text("Device Institution"), sg.Input(key='institution', readonly=True)],
        [sg.Text("Network SSID"), sg.Input(key='wifiSSID')],
        [sg.Text("Network Password"), sg.Input(key='wifiPSK')],
        [sg.Text("OSC IP 1"), sg.Input(key='oscIP1')],
        [sg.Text("OSC Port 1"), sg.Input(key='oscPORT1')],
        [sg.Text("OSC IP 2"), sg.Input(key='oscIP2')],
        [sg.Text("OSC Port 2"), sg.Input(key='oscPORT2')],
        [sg.Text("Local Port"), sg.Input(key='localPORT')],
    ]
    # Create the Window
    window = sg.Window('Serial Communicator', [[sg.Column(layout), sg.Column(config_layout)]], resizable=True, finalize=True)
    while True:
        event, values = window.read() 
        if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
            break
        elif event == 'Open':
            port = ports_dropdown.get()
            ser.port = port
            if not ser.is_open:
                ser.open()
            open_port.update(f'Current port: {port}')
            for button in buttons:
                button.update(disabled=False)
        elif event == 'Send':
            message = send_message_box.get()
            ser.write(bytes(message, 'utf-8'))
            recv_message_box.print(f'{message}', t='red')
        elif event == 'Refresh':
            ports = serial.tools.list_ports.comports()
            ports_dropdown.update(values=[port for (port, desc, hwid) in ports])
        elif event == 'Settings':
            ser.write(bytes('sendsettings ' + read_json('settings.json'), 'utf-8'))
        elif event == 'Config':
            ser.write(bytes('sendconfig ' + read_json('config.json'), 'utf-8'))
    window.close()

def read_json(filename):
    with open(filename) as f:
        return json.dumps(json.loads(f.read()))

def serial_daemon():
    while True:
        if not ser.is_open:
            sleep(1)
            continue
        data = ser.readline().decode('utf-8', 'backslashreplace')
        # recv_message_box.print(data)
        print(data)


def main():
    w = threading.Thread(target=window_function)
    w.start()
    x = threading.Thread(target=serial_daemon, daemon=True)
    x.start()


if __name__ == '__main__':
    main()