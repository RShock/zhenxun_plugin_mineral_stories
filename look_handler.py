from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.adapters.onebot.v11 import MessageSegment

from utils.message_builder import image
from .player_handler import get_player
from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo, Compose
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid, get_image
from .game_handler import Item


async def handle_look(event, item_name) -> [str, bool, list[str]]:
    player = await get_player(event)
    item_list = Stream(player.collection.keys()).filter(lambda name: item_name in name).to_list()
    if len(item_list) == 0:
        return "没有找到相关物品，你只能查阅自己曾经解锁过的物品哦"
    if len(item_list) == 1:
        return await show_info(event, item_list[0]), True, None
    return convert_items_to_str_list(item_list), False, item_list


def convert_items_to_str_list(tmp: list[str]) -> str:
    ans = "查询物品列表：\n"
    i = 0

    for item in tmp:
        ans += f"{i}: {item}\n"
        i += 1
    return ans


async def show_info(event, name):
    player = await get_player(event)
    item = get_world_data().get_item(name)
    return Message.template("{}\n{}\n{}\n历史获得数量{}").format(name, item.description,
                                                           get_image(name), str(player.collection.get(name)))
