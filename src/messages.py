import capnp

from entities import Archer
from entities import Player, Skeleton, Projectile, Coin

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
    # for i, entity in enumerate(entities):
    for i in range(len(entities)):
        if entities[i].state is not None and entities[i].direction is not None:
            if isinstance(entities[i], Player):
                update.entitiesUpdate[i] = create_entity(entities[i].uid, "player", entities[i].state.value[0],
                                                         entities[i].direction.value,
                                                         entities[i].center_x, entities[i].center_y)
            elif isinstance(entities[i], Skeleton):
                update.entitiesUpdate[i] = create_entity(entities[i].uid, "skeleton", entities[i].state.value[0],
                                                         entities[i].direction.value,
                                                         entities[i].center_x, entities[i].center_y)
            elif isinstance(entities[i], Archer):
                update.entitiesUpdate[i] = create_entity(entities[i].uid, "archer", entities[i].state.value[0],
                                                         entities[i].direction.value,
                                                         entities[i].center_x, entities[i].center_y)
        if isinstance(entities[i], Projectile):
            update.entitiesUpdate[i] = create_bullet_entity(entities[i].uid, "bullet", entities[i].center_x,
                                                            entities[i].center_y)

        if isinstance(entities[i], Coin):
            update.entitiesUpdate[i] = create_bullet_entity(entities[i].uid, "coin", entities[i].center_x,
                                                            entities[i].center_y)

    return update


def create_entity(entity_id: int, entity_type: str, state, direction, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, type=entity_type, animationstate=state,
                                                        direction=direction, x=x, y=y)


def create_bullet_entity(entity_id: int, entity_type: str, x: float, y: float):
    return server_update_capnp.EntityUpdate.new_message(id=entity_id, type=entity_type, x=x, y=y)


def read_client_update(b: bytes):
    return client_update_capnp.ClientUpdate.from_bytes_packed(b)


def read_identification_request(b: bytes):
    return identification_capnp.IdentificationRequest.from_bytes_packed(b)


def create_identification_response_failure(reason: str):
    res = identification_capnp.IdentificationResponse.new_message()
    res.failure.reason = reason
    return res


def create_identification_response_success(player_id: int):
    return identification_capnp.IdentificationResponse.new_message(
        success=identification_capnp.SuccessInformation.new_message(playerid=player_id))


def create_empty_identification_response_success():
    return identification_capnp.IdentificationResponse.new_message(
        success=identification_capnp.SuccessInformation.new_message())
