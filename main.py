from world import PersistentWorld
from entities import *
from typing import Optional
import time, sys
import socket, base64
import threading
import json

HOST : str = '127.0.0.1'
PORT : int = 8080

def read_message(sock : socket.socket) -> str:
    """
    Messages will be base64 encoded strings terminated by '\\n' character

    This way we don't need to futz with message length -- just read byte by byte until
    we find a \\n.
    """

    # Byte string we will accumulate into.
    message = b''

    while True:
        byte = sock.recv(1)
        if byte == b'\n':
            break
        else:
            message += byte

    # Convert to string:
    return base64.b64decode(message).decode('unicode_escape')

def write_message(sock : socket.socket, message : str):
    """
    Convert message to base64 bytestring and send over the wire
    """
    encoded = base64.b64encode(message.encode()) + b'\n'
    sock.sendall(encoded)

def command_server(world : PersistentWorld) -> None:
    """
    """
    print("starting command server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST,PORT))
        sock.listen()


        while True:
            conn : Optional[socket.socket] = None
            conn, _ = sock.accept()

            try: 
                with conn:
                    msg = read_message(conn)
                    # Do things with message here:
                    if msg == "get_players":
                        players = world.get_players()
                        write_message(conn, json.dumps(players))
                    elif msg.startswith("create_player"):
                        name = msg.split(' ')[1]
                        error = world.create_player(name)
                        if error is not None:
                            write_message(conn, f"error: {error}")
                        else:
                            write_message(conn, "Player created")
                    else:
                        write_message(conn, "Error: Invalid command")
                    

            except KeyboardInterrupt:
                print("ending command server")
                if conn:
                    conn.close()
                break

if __name__ == "__main__":

    world = PersistentWorld()

    world.interval = 3
    world.path = "/home/envtest/coding/blightbuddies/instance"

    listen_thread = threading.Thread(target=command_server, args=[world])
    listen_thread.start()

    if not world.load():
        print("No save loaded, creating new")
        world.create_entity(Owner(name="Peter"), Egg())
    else:
        print("Save loaded")

    world.add_processor(EggProcessor())
    while True:
        try:
            world.process()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Saving, closing")
            world.save()
            sys.exit()

