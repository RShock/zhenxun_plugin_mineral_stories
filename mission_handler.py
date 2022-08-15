import math
import random

from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .game_handler import Item
from .game_handler import get_world_data, Compose
from .player_handler import get_player
from .player_model import PlayerDB
from .stream import Stream


def check(player: PlayerDB, t: Compose) -> bool:
    if player.lv < t.lv:
        return False
    for consume in t.consume:
        if not player.collection.get(consume["name"]):
            return False
    return True
