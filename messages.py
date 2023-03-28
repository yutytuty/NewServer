import arcade
import capnp

from entities import AEntity

capnp.remove_import_hook()
server_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/server_update.capnp")


# def create_empty_server_update():
#     return server_update_capnp.ServerUpdate.new_message()


def create_entity_update(enemies: list[AEntity]):
    update = server_update_capnp.ServerUpdate.new_message()
    update.init("entitiesUpdate", len(enemies))
    for i, enemy in enumerate(enemies):
        update.entitiesUpdate[i] = create_entity(enemy.uid, enemy.center_x, enemy.center_y)


def create_entity(entity_id: int, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, x=x, y=y)
