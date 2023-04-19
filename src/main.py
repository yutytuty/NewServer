import random
import socket
import threading
from uuid import UUID

import arcade
from pyglet.math import Vec2

import constants
import messages
import users
from entities import Player, Skeleton, Projectile, Coin
from users import register, check_login

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", constants.PORT))
s.listen(5)


class World(arcade.Window):
    SKELETON_AMOUNT = 100
    SLIME_AMOUNT = 0
    ARCHER_AMOUNT = 0

    COIN_AMOUNT = 100

    def __init__(self):
        super().__init__()

        self.players = arcade.SpriteList(use_spatial_hash=True)
        self.player_projectiles = arcade.SpriteList(use_spatial_hash=True)
        self.enemies = arcade.SpriteList(use_spatial_hash=True)
        self.dead_enemies = arcade.SpriteList(use_spatial_hash=True)
        self.coins = arcade.SpriteList(use_spatial_hash=True)
        self.current_uid = 1
        self.current_uid_lock = threading.Lock()

        for i in range(World.SKELETON_AMOUNT):
            skeleton = Skeleton(self.current_uid, self.players, self.enemies, self.player_projectiles, self.dead_enemies)
            self.current_uid_lock.acquire()
            self.current_uid += 1
            self.current_uid_lock.release()
            self.enemies.append(skeleton)

        for i in range(World.COIN_AMOUNT):
            self.current_uid_lock.acquire()
            self.current_uid += 1
            x = random.randint(constants.ITEM_SPAWN_LOCATION_RANGE_MIN, constants.ITEM_SPAWN_LOCATION_RANGE_MAX)
            y = random.randint(constants.ITEM_SPAWN_LOCATION_RANGE_MIN, constants.ITEM_SPAWN_LOCATION_RANGE_MAX)
            coin = Coin(self.current_uid, x, y)
            self.current_uid_lock.release()
            self.coins.append(coin)

        self.players_to_add = []

    def on_update(self, delta_time: float):
        for player in self.players_to_add:
            self.players.append(player)
        self.players_to_add.clear()

        self.players.on_update(delta_time)
        self.enemies.on_update(delta_time)
        self.dead_enemies.on_update(delta_time)
        self.player_projectiles.on_update(delta_time)

    def get_visible_entities_for_player(self, player: Player):
        entities_in_rect = []
        rect = [player.center_x - constants.SCREEN_WIDTH / 2,
                player.center_x + constants.SCREEN_WIDTH / 2,
                player.center_y - constants.SCREEN_HEIGHT / 2,
                player.center_y + constants.SCREEN_HEIGHT / 2]
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.players))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.enemies))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.player_projectiles))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.dead_enemies))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.coins))
        return entities_in_rect

    def check_movement(self, player: Player, new_x, new_y):
        pass


def handle_client(conn: socket.socket, addr):
    print(f"[{addr}] Received connection")
    player: Player | None = None
    uuid: UUID | None = None

    start_x, start_y, resp = -1, -1, None  # just to make PyCharm not mad at me. Does not actually do anything.
    # noinspection PyBroadException
    try:
        login_request = messages.read_identification_request(conn.recv(constants.BUFFER_SIZE))
        if login_request.register:
            uuid = register(login_request.username, login_request.password)
            start_x = random.randint(constants.PLAYER_SPAWN_LOCATION_RANGE_MIN,
                                     constants.PLAYER_SPAWN_LOCATION_RANGE_MAX)
            start_y = random.randint(constants.PLAYER_SPAWN_LOCATION_RANGE_MIN,
                                     constants.PLAYER_SPAWN_LOCATION_RANGE_MAX)
            if uuid:
                resp = messages.create_empty_identification_response_success()
            else:
                resp = messages.create_identification_response_failure("usernameTaken")
        else:
            try:
                result = check_login(login_request.username, login_request.password)
                if result:
                    uuid, start_x, start_y = result
                    resp = messages.create_empty_identification_response_success()
                else:
                    resp = messages.create_identification_response_failure("invalidCredentials")
            except users.UserAlreadyLoggedInError:
                resp = messages.create_identification_response_failure("userAlreadyLoggedIn")
        if resp.which() == "failure":
            print(f"[{addr}] Sending {resp}")
            conn.send(resp.to_bytes_packed())
            print(f"[{addr}] Closing connection")
            quit()

        world.current_uid_lock.acquire()
        player = Player(world.current_uid, start_x, start_y, world.coins)
        resp.success.playerid = player.uid
        print(f"[{addr}] Sending {resp}")
        conn.send(resp.to_bytes_packed())
        world.current_uid += 1
        world.current_uid_lock.release()
        world.players_to_add.append(player)

        users.set_lock_for_user(uuid, True)
        print(f"[{addr}] locked user with uuid", str(uuid))
        print(f"[{addr}] String server update loop")
        while True:
            entities_to_send = world.get_visible_entities_for_player(player)
            server_update = messages.create_entity_update(entities_to_send)
            conn.send(server_update.to_bytes_packed())
            data = messages.read_client_update(conn.recv(constants.BUFFER_SIZE))
            match data.which():
                case "move":
                    update_vec = Vec2(data.move.x, data.move.y).normalize() * Player.SPEED
                    player.change_x = update_vec.x
                    player.change_y = update_vec.y
                case "shot":
                    world.current_uid_lock.acquire(blocking=True)
                    projectile = Projectile(world.current_uid, player.center_x, player.center_y, data.shot.x,
                                            data.shot.y, "player")
                    world.current_uid += 1
                    world.player_projectiles.append(projectile)
                    world.current_uid_lock.release()

    except Exception:
        if player:
            if uuid:
                users.set_last_logoff_location(uuid, player.center_x, player.center_y)
                users.set_coin_amount(uuid, player.coin_amount)
                print(f"[{addr}] Released lock for user with uuid", uuid)
                users.set_lock_for_user(uuid, False)
            world.players.remove(player)
        conn.close()
        quit()


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
