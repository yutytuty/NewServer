import arcade

import constants


def check_map_bounds(sprite: arcade.Sprite):
    if sprite.left < 0:
        sprite.left = 0
    if sprite.right > constants.MAP_WIDTH - 1:
        sprite.right = constants.MAP_WIDTH - 1

    if sprite.bottom < 0:
        sprite.bottom = 0
    if sprite.top > constants.MAP_HEIGHT - 1:
        sprite.top = constants.MAP_HEIGHT - 1
