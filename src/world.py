import threading
import random

import arcade

from src import constants


class World(arcade.Window):
    SKELETON_AMOUNT = 20
    ARCHER_AMOUNT = 15

    COIN_AMOUNT = 50

    instance = None

    def __init__(self):
        super().__init__()

        from entities import Skeleton, Archer, Coin

        self.players = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.player_projectiles = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.enemies = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.enemy_projectiles = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.dead_enemies = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.coins = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.xps = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.current_uid = 1
        self.current_uid_lock = threading.Lock()

        for i in range(World.SKELETON_AMOUNT):
            skeleton = Skeleton(self.current_uid, self.players, self.enemies,
                                self.player_projectiles, self.enemy_projectiles, self.dead_enemies)
            self.current_uid_lock.acquire()
            self.current_uid += 1
            self.current_uid_lock.release()
            self.enemies.append(skeleton)

        for i in range(World.ARCHER_AMOUNT):
            archer = Archer(self.current_uid, self.players, self.enemies,
                            self.player_projectiles, self.enemy_projectiles, self.dead_enemies)
            self.current_uid_lock.acquire()
            self.current_uid += 1
            self.current_uid_lock.release()
            self.enemies.append(archer)

        for i in range(World.COIN_AMOUNT):
            self.current_uid_lock.acquire()
            self.current_uid += 1
            x = random.randint(constants.ITEM_SPAWN_LOCATION_RANGE_MIN, constants.ITEM_SPAWN_LOCATION_RANGE_MAX)
            y = random.randint(constants.ITEM_SPAWN_LOCATION_RANGE_MIN, constants.ITEM_SPAWN_LOCATION_RANGE_MAX)
            coin = Coin(self.current_uid, x, y)
            self.current_uid_lock.release()
            self.coins.append(coin)

        self.players_to_add = []

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = World()
        return cls.instance

    def on_update(self, delta_time: float):
        for player in self.players_to_add:
            self.players.append(player)
        self.players_to_add.clear()

        self.players.on_update(delta_time)
        self.enemies.on_update(delta_time)
        self.dead_enemies.on_update(delta_time)
        self.player_projectiles.on_update(delta_time)
        self.enemy_projectiles.on_update(delta_time)

    def get_visible_entities_for_player(self, player):
        entities_in_rect = []
        rect = [player.center_x - constants.SCREEN_WIDTH / 2,
                player.center_x + constants.SCREEN_WIDTH / 2,
                player.center_y - constants.SCREEN_HEIGHT / 2,
                player.center_y + constants.SCREEN_HEIGHT / 2]
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.players))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.enemies))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.player_projectiles))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.enemy_projectiles))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.dead_enemies))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.coins))
        entities_in_rect.extend(arcade.get_sprites_in_rect(rect, self.xps))
        return entities_in_rect

    def check_movement(self, player, new_x, new_y):
        pass
