import json
import random
from enum import Enum

import arcade
from pyglet.math import Vec2

from common import check_map_bounds

fp = open("./hitboxes.json", "r")
hitboxes_json = json.load(fp)
fp.close()


class PlayerAnimationState(Enum):
    """Holds the path inside the resources folder and the amount of frames in the animation"""
    IDLE = ("idle", 8)
    WALK = ("walk", 8)


class SkeletonAnimationState(Enum):
    """Holds the path inside the resources folder and the amount of frames in the animation"""
    IDLE = ("idle", 4)
    WALK = ("walk", 12)
    ATTACK = ("attack", 13)
    DEATH = ("death", 13)


class ArcherAnimationState(Enum):
    """Holds the path inside the resources folder and the amount of frames in the animation"""
    IDLE = ("idle", 4)
    WALK = ("walk", 8)
    ATTACK = ("attack", 7)
    DEATH = ("death", 8)


class SlimeAnimationState(Enum):
    """Holds the path inside the resources folder and the amount of frames in the animation"""
    IDLE = ("idle", 1)
    WALK = ("walk", 4)
    ATTACK = ("attack", 0)
    DEATH = ("death", 0)


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"


class AEntity(arcade.Sprite):
    def __init__(self, uid, x, y):
        super().__init__(center_x=x, center_y=y)
        self.uid = uid
        self.direction = Direction.RIGHT
        self.state = None
        self.change_x = 0
        self.change_y = 0

    def get_position(self):
        return self.center_x, self.center_y


class AEnemy(AEntity):
    def __init__(self, uid, speed, enemy_array, animation_state, players: arcade.SpriteList, initial_state,
                 initial_direction, x=random.randint(0, 400), y=random.randint(0, 400)):
        super().__init__(uid, x, y)

        self.speed = speed
        self.enemy_array = enemy_array
        self.animation_state = animation_state
        self.players = players
        # distance_to_player = self.get
        # for player in self.players:
        #
        self.player_target: None | Player = None
        self.state = initial_state
        self.direction = initial_direction

        while len(arcade.check_for_collision_with_list(self, self.enemy_array)) > 1 or \
                len(arcade.check_for_collision_with_list(self, self.players)) > 0:
            self.center_x = random.randint(0, 400)
            self.center_y = random.randint(0, 400)

    def check_collision(self):
        enemy_collisions = arcade.check_for_collision_with_list(self, self.enemy_array)
        player_collisions = arcade.check_for_collision_with_list(self, self.players)

        if len(enemy_collisions) > 1 or len(player_collisions) > 0:
            self.center_x -= self.change_x
            self.center_y -= self.change_y
            self.change_x = 0
            self.change_y = 0
            self.state = self.animation_state.IDLE

    def set_animation_direction(self):
        if self.change_x < 0:
            self.direction = Direction.RIGHT
        elif self.change_x > 0:
            self.direction = Direction.LEFT
        else:
            if self.player_target:
                if self.center_x > self.player_target.center_x:
                    self.direction = Direction.RIGHT
                elif self.center_x < self.player_target.center_x:
                    self.direction = Direction.LEFT

    def set_direction_to_player(self, delta_time: float):
        if self.player_target:
            target_x = self.player_target.center_x
            target_y = self.player_target.center_y
            origin_x, origin_y = self.center_x, self.center_y

            direction = Vec2(target_x - origin_x, target_y - origin_y).normalize() * self.speed  # * delta_time
            self.change_x = direction.x
            self.change_y = direction.y

    def get_state(self):
        return self.state

    def update(self):
        pass

    def update_enemy_speed(self, delta_time: float):
        pass

    def shoot(self):
        pass


class Skeleton(AEnemy):
    SPEED = 2

    def __init__(self, uid, players: arcade.SpriteList, enemy_array: arcade.SpriteList):
        super().__init__(uid, Skeleton.SPEED, enemy_array, SkeletonAnimationState, players,
                         SkeletonAnimationState.IDLE, Direction.RIGHT)

        self.state = SkeletonAnimationState.IDLE
        self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["right"])


    def update_state(self):
        if self.change_x == 0 and self.change_y == 0:
            self.state = SkeletonAnimationState.IDLE
        else:
            self.state = SkeletonAnimationState.WALK

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.update_enemy_speed(delta_time)

        self.center_x += self.change_x
        self.center_y += self.change_y
        # print(self.center_x, self.center_y)

        self.update_direction()
        self.update_state()

        self.check_collision()

        self.set_animation_direction()
        check_map_bounds(self)

    def update_enemy_speed(self, delta_time: float):
        if not self.player_target:
            if len(self.players) > 0:
                self.player_target = self.players[0]  # TODO make closest player
                self.set_direction_to_player(delta_time)
            else:
                self.change_x = 0
                self.change_y = 0

    def update_direction(self):
        if self.change_x < 0:
            self.direction = Direction.LEFT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["left"])
        elif self.change_x > 0:
            self.direction = Direction.RIGHT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["right"])


class Player(AEntity):
    SPEED = 5

    def __int__(self, uid, x, y):
        super().__init__(uid, x, y)
        self.hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["right"])
        self.direction = Direction.RIGHT
        self.state = PlayerAnimationState.IDLE

    def update_state(self):
        if self.change_x == 0 and self.change_y == 0:
            self.state = PlayerAnimationState.IDLE
        else:
            self.state = PlayerAnimationState.WALK

    def update_direction(self):
        if self.change_x < 0:
            self.direction = Direction.LEFT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["left"])
        elif self.change_x > 0:
            self.direction = Direction.RIGHT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["right"])

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.update_player_speed(delta_time)
        # ToDo dont let the player walk wherever they want (check distance he moved and check he is not colliding

        self.update_direction()
        self.update_state()
        check_map_bounds(self)

    def update_player_speed(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # ToDo chenk collision and stuuf