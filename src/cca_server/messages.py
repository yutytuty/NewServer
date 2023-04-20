import capnp

from .entities import Player, Skeleton, Projectile

from colossalcyberadventuremessages import *

capnp.remove_import_hook()


def create_entity_update(entities):
    update = server_update.ServerUpdate.new_message()
    update.init("entitiesUpdate", len(entities))
    # for i, entity in enumerate(entities):
    for i in range(len(entities)):
        if entities[i].state is not None and entities[i].direction is not None:
            if isinstance(entities[i], Player):
                update.entitiesUpdate[i] = create_entity(entities[i].uid, "player", entities[i].state.value[0],
                                                         entities[i].direction.value,
                                                         entities[i].center_x, entities[i].center_y)
            if isinstance(entities[i], Skeleton):
                update.entitiesUpdate[i] = create_entity(entities[i].uid, "skeleton", entities[i].state.value[0],
                                                         entities[i].direction.value,
                                                         entities[i].center_x, entities[i].center_y)
        if isinstance(entities[i], Projectile):
            update.entitiesUpdate[i] = create_bullet_entity(entities[i].uid, "bullet", entities[i].center_x, entities[i].center_y)
    return update


def create_entity(entity_id: int, entity_type: str, state, direction, x: float, y: float):
    return server_update.EntityUpdate.new_message(id=entity_id, type=entity_type, animationstate=state,
                                                        direction=direction, x=x, y=y)


def create_bullet_entity(entity_id: int, entity_type: str, x: float, y: float):
    return server_update.EntityUpdate.new_message(id=entity_id, type=entity_type, x=x, y=y)


def read_client_update(b: bytes):
    return client_update.ClientUpdate.from_bytes_packed(b)


def read_identification_request(b: bytes):
    return identification.IdentificationRequest.from_bytes_packed(b)


def create_identification_response_failure(reason: str):
    res = identification.IdentificationResponse.new_message()
    res.failure.reason = reason
    return res


def create_identification_response_success(player_id: int):
    return identification.IdentificationResponse.new_message(
        success=identification.SuccessInformation.new_message(playerid=player_id))


def create_empty_identification_response_success():
    return identification.IdentificationResponse.new_message(
        success=identification.SuccessInformation.new_message())
