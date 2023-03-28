import os

from world import World

os.environ["ARCADE_HEADLESS"] = "True"

import socket
import threading

import constants
from client import handle_client

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", constants.PORT))
s.listen(5)

world = World()

try:
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()
except KeyboardInterrupt:
    s.close()
