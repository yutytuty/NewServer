import random
import socket
import threading

import arcade

import constants
import messages
import users
from entities import Player, Skeleton
from users import register, check_login

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", constants.PORT))
s.listen(5)


class World(arcade.Window):
    SKELETON_AMOUNT = 1
    SLIME_AMOUNT = 0
    ARCHER_AMOUNT = 0

    def __init__(self):
        super().__init__()

        self.players = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.current_uid = 0
        self.current_uid_lock = threading.Lock()

        for i in range(World.SKELETON_AMOUNT):
            skeleton = Skeleton(self.current_uid, self.players, self.enemies)
            self.current_uid_lock.acquire()
            self.current_uid += 1
            self.current_uid_lock.release()
            self.enemies.append(skeleton)

        self.players_to_add = []

    def on_update(self, delta_time: float):
        for player in self.players_to_add:
            self.players.append(player)
        self.players_to_add.clear()

    def get_visible_entities_for_player(self, player: Player):
        entities_in_rect = []
        rect = [player.center_x - constants.SCREEN_WIDTH / 2,
                player.center_x + constants.SCREEN_WIDTH / 2,
                player.center_y - constants.SCREEN_HEIGHT / 2,
                player.center_y + constants.SCREEN_HEIGHT / 2]
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.players))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.enemies))
        return entities_in_rect

    def check_movement(self, player: Player, new_x, new_y):
        pass


def handle_client(conn: socket.socket, addr):
    print("[*] Received connection from", addr)

    login_request = messages.read_identification_request(conn.recv(constants.BUFFER_SIZE))
    if login_request.register:
        if register(login_request.username, login_request.password):
            resp = messages.create_identification_response_success()
        else:
            resp = messages.create_identification_response_failure("usernameTaken")
    else:
        if check_login(login_request.username, login_request.password):
            resp = messages.create_identification_response_success()
        else:
            resp = messages.create_identification_response_failure("invalidCredentials")
    print("Sending", resp)
    conn.send(resp.to_bytes_packed())

    world.current_uid_lock.acquire()
    player = Player(world.current_uid, random.randint(100, 500), random.randint(100, 500))
    world.current_uid += 1
    world.current_uid_lock.release()
    world.players_to_add.append(player)

    print("String server update loop")
    while True:
        entities_to_send = world.get_visible_entities_for_player(player)
        server_update = messages.create_entity_update(entities_to_send)
        conn.send(server_update.to_bytes_packed())
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
users.init()
connection_listener = threading.Thread(target=listen_for_connections)
connection_listener.start()
world.run()
