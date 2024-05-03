import socket
import threading
import json

HOST = ''
PORT = 9000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f'Server listening on {HOST}:{PORT}')

def email_alert(message):
    message = message

# Accept transmissions over the stream
while True:
    data, address = server_socket.recvfrom(2048)
    print(data.decode('utf-8'), address)