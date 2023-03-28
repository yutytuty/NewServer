import arcade
import capnp

from entities import AEntity

capnp.remove_import_hook()
server_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/server_update.capnp")
client_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/client_update.capnp")


def create_entity_update(enemies):
    update = server_update_capnp.ServerUpdate.new_message()
    update.init("entitiesUpdate", len(enemies))
    for i, enemy in enumerate(enemies):
        update.entitiesUpdate[i] = create_entity(enemy.uid, "player", enemy.center_x, enemy.center_y)
    return update


def create_entity(entity_id: int, entity_type: str, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, type=entity_type, x=x, y=y)


def read_client_update(b: bytes):
    return client_update_capnp.ClientUpdate.from_bytes_packed(b)
