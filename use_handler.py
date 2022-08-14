from nonebot.adapters.onebot.v11 import GroupMessageEvent

from . import get_player
from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid
from .game_handler import Item


async def get_usable_item(event: GroupMessageEvent) -> [dict[str, Item], str]:
    player: PlayerDB = await get_player(event)
    tmp = Stream(player.bag.keys()).filter(lambda x: get_world_data().get_item(x).usable).to_list()
    return tmp, convert_usable_item_to_str(tmp)


def convert_usable_item_to_str(tmp) -> str:
    ans = "可使用物品列表：\n"
    i = 0
    for item in tmp:
        ans += f"{i}: {item}\n"
        i += 1
    return ans


async def use_item_handler(event, itemname, itemcnt) -> str:
    player:PlayerDB = await get_player(event)
    if itemname == '初级探险家实习证':
        if player.lv != 1:
            return "初级资格证能让角色升级到2级，你已经不是1级的角色了！"
        else:
            if player.cost_item("初级探险家实习证"):
                await player.update(lv=2, bag=player.bag).apply()
                return "升级到了等级2！可以探索更深的矿洞了"
            else:
                return "奇怪，背包里好像没有这个物品"

    # player.add_item(itemname, itemcnt)
    # await player.update(bag=player.bag, gold=player.gold + dif).apply()
    return f"未知错误，使用{itemname}失败"
