import json
import random
from enum import Enum
from math import atan2, degrees
from math import sqrt

import arcade
from pyglet.math import Vec2

from common import check_map_bounds
from src import constants

fp = open("hitboxes.json", "r")
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
    def __init__(self, uid, current_uid, x, y):
        super().__init__(center_x=x, center_y=y)
        self.uid = uid
        self.current_uid = current_uid
        self.direction = Direction.RIGHT
        self.state = None
        self.change_x = 0
        self.change_y = 0

    def get_position(self):
        return self.center_x, self.center_y


class AEnemy(AEntity):
    def __init__(self, uid, current_uid, speed, enemy_array, animation_state, players: arcade.SpriteList, initial_state,
                 initial_direction, player_projectile_list: arcade.SpriteList, enemy_projectile_list: arcade.SpriteList,
                 dead_enemies: arcade.SpriteList,
                 x=random.randint(constants.ENEMY_SPAWN_LOCATION_RANGE_MIN, constants.ENEMY_SPAWN_LOCATION_RANGE_MAX),
                 y=random.randint(constants.ENEMY_SPAWN_LOCATION_RANGE_MIN, constants.ENEMY_SPAWN_LOCATION_RANGE_MAX)):
        super().__init__(uid, current_uid, x, y)

        self.speed = speed
        self.enemy_array = enemy_array
        self.animation_state = animation_state
        self.dead_enemies = dead_enemies
        self._state = self.animation_state.IDLE
        self.players = players
        self.player_target: None | Player = None
        self.state = initial_state
        self.direction = initial_direction
        self.player_projectile_list = player_projectile_list
        self.enemmy_projectile_list = enemy_projectile_list

        while len(arcade.check_for_collision_with_list(self, self.enemy_array)) > 1 or \
                len(arcade.check_for_collision_with_list(self, self.players)) > 0:
            self.center_x = random.randint(constants.ENEMY_SPAWN_LOCATION_RANGE_MIN,
                                           constants.ENEMY_SPAWN_LOCATION_RANGE_MAX)
            self.center_y = random.randint(constants.ENEMY_SPAWN_LOCATION_RANGE_MIN,
                                           constants.ENEMY_SPAWN_LOCATION_RANGE_MAX)

    def check_collision(self):
        enemy_collisions = arcade.check_for_collision_with_list(self, self.enemy_array)
        player_collisions = arcade.check_for_collision_with_list(self, self.players)
        player_projectile_collisions = arcade.check_for_collision_with_list(self, self.player_projectile_list)

        if len(player_projectile_collisions) > 0:
            self.player_projectile_list[0].kill()
            self.state = self.animation_state.DEATH
            tmp = self
            for projectile in player_projectile_collisions:
                projectile.kill()
            self.kill()
            self.dead_enemies.append(tmp)

        elif len(enemy_collisions) >= 1 or len(player_collisions) > 0:
            self.center_x -= self.change_x
            self.center_y -= self.change_y
            self.change_x = 0
            self.change_y = 0
            self._state = self.animation_state.IDLE

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

    def __init__(self, uid, current_uid, players: arcade.SpriteList, enemy_array: arcade.SpriteList,
                 player_projectile_list: arcade.SpriteList, enemy_projectile_list: arcade.SpriteList,
                 dead_enemies: arcade.SpriteList):
        super().__init__(uid, current_uid, Skeleton.SPEED, enemy_array, SkeletonAnimationState, players,
                         SkeletonAnimationState.IDLE, Direction.RIGHT, player_projectile_list, enemy_projectile_list,
                         dead_enemies)

        self.state = SkeletonAnimationState.IDLE
        self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["right"], self.position)
        self.death_time = 0
        self.attack_time = 0

    def update_state(self, delta_time=0.0):
        distance_of_attack = 50
        top_y_distance_of_attack = 15
        bottom_y_distance_of_attack = -130
        if self.change_x == 0 and self.change_y == 0:
            if self.player_target:
                if (abs(self.player_target.center_x - self.left) <= distance_of_attack or
                    abs(self.right - self.player_target.center_x) <= distance_of_attack) and \
                        bottom_y_distance_of_attack <= self.center_y - \
                        self.player_target.center_y <= top_y_distance_of_attack:
                    self.state = SkeletonAnimationState.ATTACK
                    time_to_attack = 1.3
                    self.attack_time += delta_time
                    if self.attack_time > time_to_attack:
                        # TODO attack - remove hp...
                        self.attack_time = 0
                else:
                    self.attack_time = 0
                    self.state = SkeletonAnimationState.IDLE
            else:
                self.attack_time = 0
                self.state = SkeletonAnimationState.IDLE
        else:
            self.attack_time = 0
            self.state = SkeletonAnimationState.WALK

    def on_update(self, delta_time: float = 1 / 60) -> None:
        if self in self.dead_enemies:
            self.state = SkeletonAnimationState.DEATH
            time_to_die = 1.3
            self.death_time += delta_time
            if self.death_time > time_to_die:
                self.kill()
        else:
            self.update_enemy_speed(delta_time)

            self.center_x += self.change_x
            self.center_y += self.change_y

            self.check_collision()

            self.update_state(delta_time)
            self.update_direction()

            self.set_animation_direction()
            check_map_bounds(self)

    def update_enemy_speed(self, delta_time: float):
        if len(self.players) > 0:
            closest_player: None | Player = None
            for player in self.players:
                closest_distance = arcade.get_distance_between_sprites(self, player)
                closest_player = player
                distance_to_player = arcade.get_distance_between_sprites(self, player)
                if distance_to_player < closest_distance:
                    distance_to_player = closest_distance
                    closest_player = player
            self.player_target = closest_player
            self.set_direction_to_player(delta_time)
        else:
            self.change_x = 0
            self.change_y = 0

    def update_direction(self):
        if self.change_x < 0:
            self.direction = Direction.LEFT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["left"], self.position)
        elif self.change_x > 0:
            self.direction = Direction.RIGHT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["right"], self.position)


class Archer(AEnemy):
    SPEED = 3

    def __init__(self, uid, current_uid, players: arcade.SpriteList, enemy_array: arcade.SpriteList,
                 player_projectile_list: arcade.SpriteList, enemy_projectile_list: arcade.SpriteList,
                 dead_enemies: arcade.SpriteList):
        super().__init__(uid, current_uid, Archer.SPEED, enemy_array, ArcherAnimationState, players,
                         ArcherAnimationState.IDLE, Direction.RIGHT, player_projectile_list, enemy_projectile_list,
                         dead_enemies)

        self.state = ArcherAnimationState.IDLE
        self.hit_box = arcade.hitbox.HitBox(hitboxes_json["archer"]["right"], self.position)
        self.death_time = 0
        self.shoot_time = 0

    def update_state(self, delta_time=0.0):
        if self.change_x == 0 and self.change_y == 0:
            if self.player_target:
                max_distance_of_attack = 700
                distance_to_player = sqrt(
                    abs(self.center_x - self.player_target.center_x) ** 2 + abs(
                        self.center_y - self.player_target.center_y) ** 2)
                if distance_to_player <= max_distance_of_attack and (self.state == ArcherAnimationState.IDLE or
                                                                     self.state == ArcherAnimationState.ATTACK):
                    self.state = ArcherAnimationState.ATTACK
                    time_to_shoot = 0.7
                    self.shoot_time += delta_time
                    if self.shoot_time > time_to_shoot:
                        self.shoot()
                        self.shoot_time = 0

                else:
                    self.shoot_time = 0
                    self.state = ArcherAnimationState.IDLE
            else:
                self.shoot_time = 0
                self.state = ArcherAnimationState.IDLE
        else:
            self.shoot_time = 0
            self.state = ArcherAnimationState.WALK

    def on_update(self, delta_time: float = 1 / 60) -> None:
        if self in self.dead_enemies:
            self.state = ArcherAnimationState.DEATH
            time_to_die = 0.8
            self.death_time += delta_time
            if self.death_time > time_to_die:
                self.kill()
        else:
            self.update_enemy_speed(delta_time)

            self.center_x += self.change_x
            self.center_y += self.change_y

            self.check_collision()

            self.update_state(delta_time)
            self.update_direction()

            self.set_animation_direction()
            check_map_bounds(self)

    def update_enemy_speed(self, delta_time: float):
        if len(self.players) > 0:
            closest_player: None | Player = None
            for player in self.players:
                closest_distance = arcade.get_distance_between_sprites(self, player)
                closest_player = player
                distance_to_player = arcade.get_distance_between_sprites(self, player)
                if distance_to_player < closest_distance:
                    distance_to_player = closest_distance
                    closest_player = player
            self.player_target = closest_player

            min_distance_to_player = 300
            mam_distance_to_player = 500

            self.set_direction_to_player(delta_time)

            distance_to_player = sqrt(abs(self.player_target.center_x - self.center_x) ** 2 + abs(
                self.player_target.center_y - self.center_y) ** 2)
            if distance_to_player < min_distance_to_player:
                self.change_x = -self.change_x
                self.change_y = -self.change_y
            elif distance_to_player < mam_distance_to_player:
                self.change_x = 0
                self.change_y = 0

    def shoot(self):
        pass
        # arrow_kind = "arrow"
        # if self.direction == Direction.LEFT:
        #     source_x = self.center_x + 30
        # else:
        #     source_x = self.center_x - 30
        # projectile = Projectile(self.current_uid, self.current_uid, source_x, self.center_y, self.player_target.center_x,
        #                         self.player_target.center_y, arrow_kind)
        # # self.current_uid += 1  # TODO add lock
        # self.enemy_projectiles.append(projectile)
        # self.current_uid_lock.acquire()
        # self.current_uid += 1
        # self.current_uid_lock.release()

    def update_direction(self):
        if self.change_x < 0:
            self.direction = Direction.LEFT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["archer"]["left"], self.position)
        elif self.change_x > 0:
            self.direction = Direction.RIGHT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["archer"]["right"], self.position)


class Player(AEntity):
    SPEED = 5

    def __init__(self, uid, current_uid, x, y, coin_list: arcade.SpriteList):
        super().__init__(uid, current_uid, x, y)
        self.coin_list = coin_list
        self._hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["right"], (self.center_x, self.center_y), (2, 2))
        self.direction = Direction.RIGHT
        self.state = PlayerAnimationState.IDLE
        self.coin_amount = 0

    def update_state(self):
        if self.change_x == 0 and self.change_y == 0:
            self.state = PlayerAnimationState.IDLE
        else:
            self.state = PlayerAnimationState.WALK

    def update_direction(self):
        if self.change_x < 0:
            self.direction = Direction.LEFT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["left"], (self.center_x, self.center_y), (2, 2))
        elif self.change_x > 0:
            self.direction = Direction.RIGHT
            self.hit_box = arcade.hitbox.HitBox(hitboxes_json["player"]["right"], (self.center_x, self.center_y),
                                                (2, 2))

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.update_player_speed(delta_time)
        # # ToDo dont let the player walk wherever they want (check distance he moved and check he is not colliding
        #
        self.update_direction()
        self.update_state()
        check_map_bounds(self)

        coin_collision_list = arcade.check_for_collision_with_list(self, self.coin_list)
        if len(coin_collision_list) > 0:
            for coin in coin_collision_list:
                self.coin_amount += 1
                coin.kill()

    def update_player_speed(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # ToDo chenk collision and stuuf


class Projectile(AEntity):
    Sprite_Path = None
    SPEED = 750

    def __init__(self, uid, current_uid, origin_x: float, origin_y: float, target_x: float, target_y: float,
                 bullet_kind: str,
                 distance=700):
        super().__init__(uid, current_uid, origin_x, origin_y)
        self.distance = 0
        self.hit_box = arcade.hitbox.HitBox(hitboxes_json["skeleton"]["right"],
                                            self.position)  # TODO placeholder - make sprite
        self.max_distance = distance
        self.origin_x = origin_x
        self.origin_y = origin_y

        direction = Vec2(target_x - origin_x, target_y - origin_y).normalize() * Projectile.SPEED
        self.change_x = direction.x
        self.change_y = direction.y
        self.angle = degrees(atan2(direction.y, direction.x))

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.distance = sqrt(abs(self.origin_x - self.center_x) ** 2 + abs(self.origin_y - self.center_y) ** 2)
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        if self.distance >= self.max_distance:
            self.remove_from_sprite_lists()


class Coin(AEntity):
    def __init__(self, uid, current_uid, x, y):
        super().__init__(uid, current_uid, x, y)
