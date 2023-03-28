import socket

import constants
import messages


def handle_client(conn: socket.socket, addr):
    print("[*] Received connection from", addr)
    server_update = messages.create_empty_server_update()
    server_update.init("entitiesUpdate", 1)
    server_update.entitiesUpdate[0] = messages.create_entity(0, 0, 0)
    conn.send(server_update.to_bytes_packed())
