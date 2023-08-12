import socket
import random
import base64

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

def send_message(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        msg = base64.b64encode(str(msg).encode()) + b'\n'

        s.connect((HOST, PORT))
        s.sendall(msg)

        msg = b''
        while True:
            byte = s.recv(1)
            if byte == b'\n':
                break
            else:
                msg += byte
        data = base64.b64decode(msg)
    print(f"Received: {data}")
