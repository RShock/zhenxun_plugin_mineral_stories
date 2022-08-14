from nonebot.adapters.onebot.v11 import GroupMessageEvent

from . import get_player
from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid
from .game_handler import Item


async def get_store_list(event: GroupMessageEvent) -> [dict[str, Item], str]:
    tmp = get_world_data().get_shop_item()
    return tmp, convert_shop_item_to_str(tmp)


def convert_shop_item_to_str(tmp) -> str:
    ans = "商品列表：\n"
    i = 0
    for item in tmp:
        ans += f"{i}: {item.name}: {item.cost}金\n"
        i += 1
    return ans


async def buy_item_handle(event, itemname, itemcost, itemcnt) -> str:
    player = await get_player(event)
    dif = itemcnt * itemcost - player.gold
    if dif > 0:
        return f"你买不起这么贵的商品，还差{dif}"
    player.add_item(itemname, itemcnt)
    await player.update(bag=player.bag, gold=player.gold + dif).apply()
    return f"从老板那里获得了{itemname} x{itemcnt}"
