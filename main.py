import random
import socket
import threading

import arcade

import constants
import messages
from entities import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", constants.PORT))
s.listen(5)


class World(arcade.Window):
    def __init__(self):
        super().__init__()

        self.players = arcade.SpriteList()
        self.players_to_add = []

    def on_update(self, delta_time: float):
        for player in self.players_to_add:
            self.players.append(player)
        self.players_to_add.clear()


def handle_client(conn: socket.socket, addr):
    print("[*] Received connection from", addr)
    player = Player(len(world.players), random.randint(100, 500), random.randint(100, 500))
    world.players_to_add.append(player)

    while True:
        conn.send(messages.create_entity_update(world.players).to_bytes_packed())
        data = messages.read_client_update(conn.recv(constants.BUFFER_SIZE))
        match data.which():
            case "move":
                player.center_x = data.move.x
                player.center_y = data.move.y


def listen_for_connections():
    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
    except KeyboardInterrupt:
        arcade.exit()


world = World()
connection_listener = threading.Thread(target=listen_for_connections)
connection_listener.start()
world.run()
