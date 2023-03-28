import arcade


class AEntity(arcade.Sprite):
    def __init__(self, uid):
        super().__init__()
        self.uid = uid


class Slime(AEntity):
    def __init__(self, uid):
        super().__init__(uid)
