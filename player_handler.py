import asyncio

from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .adv_handler import get_user_status
from .player_model import PlayerDB
from .utils import get_uid


async def register_new_player(event: GroupMessageEvent, name, sex) -> str:
    player = await PlayerDB.get_player_by_name(name)
    if player:
        return "这个名字已经有人用过啦！"

    player = await PlayerDB.register(get_uid(event), event.group_id, name, sex)
    if player:
        return f"{name}({sex},探险等级{player.lv})加入了矿石物语的世界！你是第{player.id}个玩家哦\n" \
               f"输入【领取任务】指令开始你的新手引导吧！"
    else:
        return "未知错误..."


async def get_player(event) -> PlayerDB:
    player = await PlayerDB.get_player_by_uid(get_uid(event))
    return player


async def get_user_status_str(event) -> str:
    player, status, pos_list = await get_user_status(event)
    return f"{player.name} lv{player.lv} {player.sex} {status}\n" \
           f"装备：\n" \
           f"{player.show_equip()}\n" \
           f"背包：\n" \
           f"{player.showbag()}"
