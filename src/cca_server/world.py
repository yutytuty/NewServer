class World:
	"""Manage al the sprites"""

	def __init__(self) -> None:
		self.players = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.player_projectiles = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.enemies = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.dead_enemies = arcade.SpriteList(use_spatial_hash=True, lazy=True)
