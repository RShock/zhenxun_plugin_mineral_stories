from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid
from .game_handler import Item


async def get_store_list(event: GroupMessageEvent) -> [dict[str, Item], str]:
    tmp = get_world_data().get_shop_item()
    return tmp, convert_shop_item_to_str(tmp)


def convert_shop_item_to_str(tmp: dict[str, Item]) -> str:
    ans = "商品列表：\n"
    i = 0
    for k, v in tmp.items():
        ans += f"{i}: {k} {v.cost}金\n"
    return ans

async def get_store_list(event: GroupMessageEvent) -> [dict[str, Item], str]:
    tmp = get_world_data().get_shop_item()
    return tmp, convert_shop_item_to_str(tmp)
    buy_item_handle