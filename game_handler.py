import asyncio
import types

from models.bag_user import BagUser
from configs.config import Config
from .player_model import PlayerDB
from services.log import logger
import json
import os

from .stream import Stream


class Map:
    name = '未定义地图'  # 地图名称
    mineral_list = {}  # 地图拥有的矿物和概率
    owned = {}  # 子地图
    require_level = 1  # 地图需要的探索等级
    require_honor = {}  # 地图需要的特别称号
    require_buff = {}  # 地图需要的特别buff
    require_item = {}  # 地图需要的特别物品
    cost = {}  # 地图的消耗
    public = True  # 是否直接可达
    description = "未填写"


class Item:
    name = '未定义物品'  # 地图名称
    description = "未填写"
    cost = None  # 如果填写cost 就会被商店出售
    lv = 0
    usable = False

    def simple_name(self):
        return f"{self.name}(Lv.{self.lv})"


class Compose:
    name = '未定义合成表'
    lv: 1
    type = '熔炼'
    consume = []
    produce = []
    time_cost = 1


class WorldInfo:
    mapList: dict[str, Map]
    itemList: dict[str, Item]
    forgeList: list[Compose]

    def get_item(self, name) -> Item:
        return self.itemList.get(name)

    def get_map(self, name) -> Map:
        return self.mapList.get(name)

    def get_shop_item(self):  # 如果填写cost 就会被商店出售
        return Stream(self.itemList.items()).map(lambda i: i[1]).filter(lambda i: i.cost).to_list()

    def get_forge_list(self):
        return self.forgeList

    def get_forge(self, name:str):
        return Stream(self.forgeList).filter(lambda f: f.name == name).find_first()


world_data: WorldInfo


def get_world_data() -> WorldInfo:
    return world_data


async def load_world_data() -> None:
    global world_data
    world_data = WorldInfo()
    logger.info(f'矿石物语资源载入中')
    path = os.path.dirname(__file__) + '/gamedata'
    files = os.listdir(path)
    for file in files:
        # try:
        with open(f'{path}/{file}', "r", encoding="utf-8") as f:
            if file == '地图.json':
                world_data.mapList = parse_map(json.load(f))
                logger.info(f'地图载入完成，共{len(world_data.mapList)}张地图')
            if file == '物品.json':
                world_data.itemList = parse_item(json.load(f))
                logger.info(f'物品载入完成，共{len(world_data.itemList)}个物品')
            if file == '制作表.json':
                world_data.forgeList = parse_compose(json.load(f))
                logger.info(f'制作表载入完成，共{len(world_data.forgeList)}个配方')


def parse_map(map_json):
    map_list = {}
    for key, value in map_json.items():
        mp = Map()
        mp.name = key
        mp.require_level = value["require_level"]
        mp.owned = value.get("owned") or {}  # 可为空 下同
        mp.mineral_list = value.get("mineral_list") or {}
        mp.public = value["public"]
        mp.require_honor = value.get("require_honor") or {}
        mp.require_buff = value.get("require_buff") or {}
        mp.require_item = value.get("require_item") or {}
        mp.description = value.get("description") or {}
        mp.cost = value.get("cost") or {}
        map_list[key] = mp

        if not isinstance(mp.owned, dict):
            logger.warning(f"地图类型疑似错误：{mp.owned}")
        if not isinstance(mp.mineral_list, list):
            logger.warning(f"地图类型疑似错误：{mp.mineral_list}")
    return map_list


def parse_item(item_json):
    item_list = {}
    for key, value in item_json.items():
        item = Item()
        item.name = key
        item.description = value["des"]
        item.lv = value["lv"]
        item.usable = value.get("usable")
        item.cost = value.get("cost")
        item_list[key] = item

    return item_list


def parse_compose(compose_json):
    compose_list = []
    for v in compose_json:
        comp = Compose()
        comp.name = v["name"]
        comp.lv = v["lv"]
        comp.type = v.get("type") or "熔炼"
        comp.time_cost = v["time_cost"]
        comp.consume = v["consume"]
        comp.produce = v["produce"]
        compose_list.append(comp)

    return compose_list
