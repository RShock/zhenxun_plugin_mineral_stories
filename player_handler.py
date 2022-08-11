import asyncio

from nonebot.adapters.onebot.v11 import GroupMessageEvent

from models.bag_user import BagUser
from configs.config import Config
from .player_model import PlayerDB
from .utils import get_uid


async def register_new_player(event: GroupMessageEvent, name, sex) -> str:
    player = await PlayerDB.get_player_by_name(name)
    if player:
        return "这个名字已经有人用过啦！"

    player = await PlayerDB.register(get_uid(event), event.group_id, name, sex)
    if player:
        return f"{name}({sex},探险等级{player.lv})加入了矿石物语的世界！你是第{player.id}个玩家哦"
    else:
        return "未知错误..."


async def get_player(event) -> PlayerDB:
    player = await PlayerDB.get_player_by_uid(get_uid(event))
    return player


async def buy_item_handle(event, itemname, itemcnt) -> str:
    return ""


