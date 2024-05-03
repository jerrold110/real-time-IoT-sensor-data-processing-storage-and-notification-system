import socket
import threading
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('server', 9000)
message = json.dumps({'sensor_id':1, 'timestamp':'abc'})

try:
    client_socket.sendto(message.encode('utf-8'), server_address)
    print('message sent to server')
finally:
    client_socket.close()