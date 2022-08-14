from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .player_handler import get_player
from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo, Compose
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid
from .game_handler import Item


def check(player: PlayerDB, t: Compose) -> bool:
    if player.lv < t.lv:
        return False
    for consume in t.consume:
        if not player.collection.get(consume["name"]):
            return False
    return True


async def get_forge_list(event: GroupMessageEvent) -> [dict[str, Item], str]:
    tmp = get_world_data().get_forge_list()
    player = await get_player(event)
    tmp = Stream(tmp).filter(lambda t: check(player, t)).to_list()
    return tmp, convert_shop_item_to_str(tmp)


def convert_shop_item_to_str(tmp: list[Compose]) -> str:
    ans = "制作列表：\n"
    i = 0
    for item in tmp:
        ans += f"{i}: {item.name}\n"
        i += 1
    return ans


async def handle_forge(event, forge) -> str:
    return f'开始{forge["type"]}了({forge["name"]})！'
