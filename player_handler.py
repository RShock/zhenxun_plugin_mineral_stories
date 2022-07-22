import asyncio

from models.bag_user import BagUser
from configs.config import Config
from .player_model import PlayerDB


async def register_new_player(event, name, sex) -> str:
    player = await PlayerDB.get_player_by_name(name)
    if player:
        return "这个名字已经有人用过啦！"

    player = await PlayerDB.register(get_uid(event), name, sex)
    if player:
        return f"{name}({sex},探险等级{player.lv})加入了矿石物语的世界！"
    else:
        return "未知错误..."


async def check_register(event) -> bool:
    player = await PlayerDB.get_player_by_uid(get_uid(event))
    return player


def get_uid(event) -> str:
    return f"{event.user_id}:{event.group_id}"
