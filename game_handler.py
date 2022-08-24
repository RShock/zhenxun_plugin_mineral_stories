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
    equip_type = None

    def simple_name(self):
        return f"{self.name}(Lv.{self.lv})"


class Compose:
    name = '未定义合成表'
    lv: 1
    type = '熔炼'
    consume = []
    produce = []


class Mission:
    name = '未定义名称'
    type = '未定义类型'
    repeatable: bool = False
    hide_reward: bool = False
    des = '未定义任务描述'
    tar = '未定义任务目标'
    check = {}
    hint = '未定义任务提示'
    reward: dict[str, int] = {}
    next = '未定义下一个任务'


class WorldInfo:
    mapList: dict[str, Map]
    itemList: dict[str, Item]
    forgeList: list[Compose]
    missionList: dict[str, Mission]

    def get_item(self, name) -> Item:
        return self.itemList.get(name)

    def get_map(self, name) -> Map:
        return self.mapList.get(name)

    def get_shop_item(self):  # 如果填写cost 就会被商店出售
        return Stream(self.itemList.items()).map(lambda i: i[1]).filter(lambda i: i.cost).to_list()

    def get_forge_list(self) -> list[Compose]:
        return self.forgeList

    def get_forge(self, name: str):
        return Stream(self.forgeList).filter(lambda f: f.name == name).find_first()

    def get_mission_list(self) -> dict[str, Mission]:
        return self.missionList

    def get_mission(self, name) -> Mission:
        return self.missionList.get(name)


world_data: WorldInfo


def get_world_data() -> WorldInfo:
    return world_data


async def load_world_data() -> None:
    global world_data
    world_data = WorldInfo()
    logger.info(f'矿石物语资源载入中')
    path = os.path.dirname(__file__) + '/gamedata/json'
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
            if file == '任务.json':
                world_data.missionList = parse_mission(json.load(f))
                logger.info(f'任务载入完成，共{len(world_data.missionList)}个任务')

    # 校验制作表内的道具是否在物品栏内 稍微有点废资源 问题不大
    for j in world_data.forgeList:
        for i in j.consume:
            if get_world_data().get_item(i["name"]) is None:
                logger.warning(f"制作表内出现未知道具:{i['name']}")
        for i in j.produce:
            if get_world_data().get_item(i["name"]) is None:
                logger.warning(f"制作表内出现未知道具:{i['name']}")


def parse_map(map_json):
    map_dict = {}
    for key, value in map_json.items():
        mp = Map()
        mp.name = key
        mp.require_level = value["require_level"]
        mp.owned = value.get("owned") or []  # 可为空 下同
        mp.mineral_list = value.get("mineral_list", [])
        mp.public = value["public"]
        mp.require_honor = value.get("require_honor", {})
        mp.require_buff = value.get("require_buff", {})
        mp.require_item = value.get("require_item", {})
        mp.description = value.get("description", {})
        mp.cost = value.get("cost", {})
        map_dict[key] = mp

        if not isinstance(mp.owned, list):
            logger.warning(f"地图类型疑似错误：{mp.owned}")
        if not isinstance(mp.mineral_list, list):
            logger.warning(f"地图类型疑似错误：{mp.mineral_list}")
    return map_dict


def parse_item(item_json):
    item_dict = {}
    for key, value in item_json.items():
        item = Item()
        item.name = key
        item.description = value["des"]
        item.lv = value["lv"]
        item.usable = value.get("usable")
        item.cost = value.get("cost")
        item.equip_type = value.get('equip_type')
        item_dict[key] = item

    return item_dict


def parse_compose(compose_json):
    compose_list = []
    for v in compose_json:
        comp = Compose()
        comp.name = v["name"]
        comp.lv = v["lv"]
        comp.type = v.get("type", "熔炼")
        comp.consume = v["consume"]
        comp.produce = v["produce"]
        compose_list.append(comp)

    return compose_list


def parse_mission(mission_json):
    mission_dict = {}
    for v in mission_json:
        mission = Mission()
        mission.name = v["name"]
        mission.type = v["type"]
        if not mission.type in ["主线", "支线", "世界任务"]:
            logger.warning(f"未知任务类型{mission.type}")
        mission.repeatable = v.get("repeatable", "不可领取")
        mission.des = v["des"]
        mission.tar = v["tar"]
        mission.hint = v["hint"]
        mission.reward = v.get("reward", {})
        mission.next = v.get("next")
        mission.check = v["check"]
        mission.hide_reward = v.get("hide_reward")
        mission_dict[mission.name] = mission

    return mission_dict
