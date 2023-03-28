import capnp

capnp.remove_import_hook()
server_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/server_update.capnp")


def create_empty_server_update():
    return server_update_capnp.ServerUpdate.new_message()


def create_entity(entity_id: int, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, x=x, y=y)
