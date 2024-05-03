import socket
import threading
import json
import smtplib
# Maybe use multithreading to handle multiple actions at the same time

HOST = ''
PORT = 9000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

def email_alert(string):
    data = json.loads(string)
    sensor_id = data['sensor_id']
    timestamp = data['timestamp']

    # Use SMTP library to send an email to notify sensor has overheated, and something to turn off machine

while True:
    data, address = server_socket.recvfrom(2048)
    email_alert(data.decode('utf-8'))