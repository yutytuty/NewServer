import json

import arcade


fp = open("./hitboxes.json", "r")
hitboxes_json = json.load(fp)
fp.close()


class AEntity(arcade.Sprite):
    def __init__(self, uid, x, y):
        super().__init__(center_x=x, center_y=y)
        self.uid = uid


class Slime(AEntity):
    def __init__(self, uid, x, y):
        super().__init__(uid, x, y)


class Player(AEntity):
    def __int__(self, uid, x, y):
        super().__init__(uid, x, y)

        self.hit_box = hitboxes_json["player"]
