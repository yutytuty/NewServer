import random
import socket
import threading
from queue import Queue
from uuid import UUID

import arcade
from pyglet.math import Vec2

import constants
import messages
import users
from users import register, check_login
from world import World

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", constants.PORT))
s.listen(5)


def handle_client(conn: socket.socket, addr):
    global coin_queue
    from entities import Player, Projectile
    print(f"[{addr}] Received connection")
    player: Player | None = None
    uuid: UUID | None = None

    start_x, start_y, resp = -1, -1, None  # just to make PyCharm not mad at me. Does not actually do anything.
    # noinspection PyBroadException
    try:
        login_request = messages.read_identification_request(conn.recv(constants.BUFFER_SIZE))
        if login_request.register:
            uuid = register(login_request.username, login_request.password)
            start_x = random.randint(constants.PLAYER_SPAWN_LOCATION_RANGE_MIN_X,
                                     constants.PLAYER_SPAWN_LOCATION_RANGE_MAX_X)
            start_y = random.randint(constants.PLAYER_SPAWN_LOCATION_RANGE_MIN_X,
                                     constants.PLAYER_SPAWN_LOCATION_RANGE_MAX_X)
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

        World.get_instance().current_uid_lock.acquire()
        world = World.get_instance()
        player = Player(world.current_uid, start_x, start_y, World.get_instance().coins, world.enemies, world.players,
                        world.player_projectiles, world.enemy_projectiles)
        resp.success.playerid = player.uid
        coin_amount = users.get_coin_amount(uuid)
        xp_amount = users.get_xp_amount(uuid)
        mushroom_amount = users.get_mushroom_amount(uuid)
        hp_amount = users.get_hp_amount(uuid)
        resp.success.coinamount = coin_amount
        resp.success.xpamount = xp_amount
        resp.success.mushroomamount = mushroom_amount
        resp.success.hpamount = hp_amount
        player.coin_amount = coin_amount
        player.xp_amount = xp_amount
        player.mushroom_amount = mushroom_amount
        player.hp = hp_amount
        print(f"[{addr}] Sending {resp}")
        conn.send(resp.to_bytes_packed())
        World.get_instance().current_uid += 1
        World.get_instance().current_uid_lock.release()
        World.get_instance().players_to_add.append(player)

        users.set_lock_for_user(uuid, True)
        print(f"[{addr}] locked user with uuid", str(uuid))
        print(f"[{addr}] String server update loop")
        while True:
            # entities:
            entities_to_send = World.get_instance().get_visible_entities_for_player(player)
            server_update = messages.create_entity_update(entities_to_send)
            conn.send(server_update.to_bytes_packed())

            # items:
            if player.should_update_coin_amount:
                item_update = messages.create_item_update("coin", 1)
                conn.send(item_update.to_bytes_packed())
                player.should_update_coin_amount = False
            if player.should_update_xp_amount:
                item_update = messages.create_item_update("xp", 1)
                conn.send(item_update.to_bytes_packed())
                player.should_update_xp_amount = False
            if player.should_add_to_mushroom_amount:
                item_update = messages.create_item_update("mushroom", 1)
                conn.send(item_update.to_bytes_packed())
                player.should_add_to_mushroom_amount = False
            if player.should_reduce_mushroom_amount:
                item_update = messages.create_item_update("mushroom", -1)
                conn.send(item_update.to_bytes_packed())
                player.should_reduce_mushroom_amount = False
            if player.should_update_health_amount:
                health_update = messages.create_health_update(player.hp)
                conn.send(health_update.to_bytes_packed())
                player.should_update_health_amount = False
            data = messages.read_client_update(conn.recv(constants.BUFFER_SIZE))
            match data.which():
                case "move":
                    update_vec = Vec2(data.move.x, data.move.y).normalize() * Player.SPEED
                    player.change_x = update_vec.x
                    player.change_y = update_vec.y
                case "shot":
                    World.get_instance().current_uid_lock.acquire(blocking=True)
                    projectile = Projectile(World.get_instance().current_uid, player.center_x, player.center_y,
                                            data.shot.x,
                                            data.shot.y, "player")
                    World.get_instance().current_uid += 1
                    World.get_instance().player_projectiles.append(projectile)
                    World.get_instance().current_uid_lock.release()
                case "useSkill":
                    skill_num = data.useSkill
                    if skill_num == 1:
                        player.on_skill_1()
                    if skill_num == 2:
                        player.on_skill_2()
                    if skill_num == 3:
                        player.on_skill_3()
                case "useItem":
                    item = data.useItem
                    if item == "mushroom":
                        player.use_mushroom()

    except Exception as e:
        print(e)
        if player:
            if uuid:
                users.set_last_logoff_location(uuid, player.center_x, player.center_y)
                users.set_coin_amount(uuid, player.coin_amount)
                users.set_xp_amount(uuid, player.xp_amount)
                users.set_mushroom_amount(uuid, player.mushroom_amount)
                users.set_hp_amount(uuid, player.hp)
                print(f"[{addr}] Released lock for user with uuid", uuid)
                users.set_lock_for_user(uuid, False)
                if player.hp <= 0:
                    print(f"[{addr}] Resetting stats for user with uuid", uuid)
                    users.reset_stats(uuid)
            World.get_instance().players.remove(player)
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


print(0)
users.init()
print(1)
connection_listener = threading.Thread(target=listen_for_connections)
print(2)
connection_listener.start()
print(3)
World.get_instance().run()
