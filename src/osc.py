from pythonosc import dispatcher
from pythonosc import osc_server

def handle_data(unused_addr, args, data):
    print(f"Received data2: {data}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/pressure", handle_data, "Data")

server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8005), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()

#nothing