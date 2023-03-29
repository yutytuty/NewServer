import capnp

from entities import Player, Skeleton

capnp.remove_import_hook()
server_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/server_update.capnp")
client_update_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/client_update.capnp")
identification_capnp = capnp.load(
    "ColossalCyberAdventureMessages/src/colossalcyberadventuremessages/identification.capnp")


def create_entity_update(entities):
    update = server_update_capnp.ServerUpdate.new_message()
    update.init("entitiesUpdate", len(entities))
    for i, entity in enumerate(entities):
        if isinstance(entity, Player):
            update.entitiesUpdate[i] = create_entity(entity.uid, "player", entity.center_x, entity.center_y)
        if isinstance(entity, Skeleton):
            update.entitiesUpdate[i] = create_entity(entity.uid, "skeleton", entity.center_x, entity.center_y)
    return update


def create_entity(entity_id: int, entity_type: str, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, type=entity_type, x=x, y=y)


def read_client_update(b: bytes):
    return client_update_capnp.ClientUpdate.from_bytes_packed(b)


def read_identification_request(b: bytes):
    return identification_capnp.IdentificationRequest.from_bytes_packed(b)


def create_identification_response_failure(reason: str):
    res = identification_capnp.IdentificationResponse.new_message()
    res.failure.reason = reason
    return res


def create_identification_response_success():
    return identification_capnp.IdentificationResponse.new_message(success=None)
