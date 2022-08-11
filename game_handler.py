import asyncio

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
    produce = {}
    cost = None  # 如果填写cost 就会被商店出售
    lv = 0

    def simple_name(self):
        return f"{self.name}(Lv.{self.lv})"


class WorldInfo:
    mapList: dict[str, Map]
    itemList: dict[str, Item]

    def get_item(self, name) -> Item:
        return self.itemList.get(name)

    def get_map(self, name) -> Map:
        return self.mapList.get(name)

    def get_shop_item(self) -> dict[[str, Item]]: # 如果填写cost 就会被商店出售
        return Stream(self.itemList.items()).filter(lambda i: i[1].cost).to_map(lambda i: i[0], lambda i: i[1])


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
        try:
            with open(f'{path}/{file}', "r", encoding="utf-8") as f:
                if file == '地图.json':
                    world_data.mapList = parse_map(json.load(f))
                    logger.info(f'地图载入完成，共{len(world_data.mapList)}张地图')
                if file == '物品.json':
                    world_data.itemList = parse_item(json.load(f))
                    logger.info(f'物品载入完成，共{len(world_data.itemList)}个物品')
                # if file == '商品.json':
                #     world_data.shop

        except:
            logger.info(f"加载 {file} 失败！")


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

    return map_list


def parse_item(item_json):
    item_list = {}
    for key, value in item_json.items():
        item = Item()
        item.name = key
        item.description = value["des"]
        item.lv = value["lv"]
        item.cost = value.get("cost")
        item.produce = value.get("produce") or {}
        item_list[key] = item

    return item_list
