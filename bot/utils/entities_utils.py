from aiogram.types import MessageEntity

import typing as t
import json


# подготавливает сущности к сохранению (превращает в список строк)
def save_entities(entities: t.Optional[list[MessageEntity]]) -> list[str]:
    entities_list = []
    if entities:
        for entity in entities:
            entities_list.append (
                json.dumps (
                    {'type': entity.type,
                     'offset': entity.offset,
                     'length': entity.length,
                     'url': entity.url,
                     'user': entity.user,
                     'language': entity.language,
                     'custom_emoji_id': entity.custom_emoji_id}
                )
            )
    return entities_list


# восстанавливает сущности
def recover_entities(entities: t.Optional[list[str]]) -> list[MessageEntity]:
    entities_list = []
    if entities:
        for entity in entities:
            entity_dict = json.loads(entity)
            entities_list.append(MessageEntity(
                type=entity_dict['type'],
                offset=entity_dict['offset'],
                length=entity_dict['length'],
                url=entity_dict['url'],
                user=entity_dict['user'],
                language=entity_dict['language'],
            ))
    return entities_list
