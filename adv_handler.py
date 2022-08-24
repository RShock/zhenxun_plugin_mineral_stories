import datetime
import json
import math
import random
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from services import db
from .adv_model import ActionDB
from .game_handler import Map, get_world_data, WorldInfo
from .player_model import PlayerDB
from .stream import Stream
from .utils import add_item, get_uid


async def get_user_can_go(player: PlayerDB):
    names = []
    for key, game_map in get_world_data().mapList.items():
        if game_map.require_level > player.lv or not game_map.public:
            continue
        names.append(key)
    return names


async def get_user_status(event) -> [PlayerDB, list[str]]:
    player = await PlayerDB.get_player_by_uid(get_uid(event))
    status = await get_player_status(event)
    pos_list = await get_user_can_go(player)
    return player, status, pos_list


async def go_outside(event: GroupMessageEvent, pos: str) -> None:
    await ActionDB.go_outside(get_uid(event), pos)


async def get_player_status(event: GroupMessageEvent) -> str:
    action = await ActionDB.get_action_by_uid(get_uid(event))
    if action is not None:
        return f"{action.action}"
    return "休息中"


async def query_status(event: GroupMessageEvent, pos: str) -> None:
    action = await ActionDB.get_action_by_uid(get_uid(event))


async def finish_action(event: GroupMessageEvent, checker) -> bool:
    action: ActionDB = await ActionDB.get_action_by_uid(get_uid(event))
    if not checker(action):
        return False
    # 把任务改成10天前触发的，这样就可以迅速完成了
    await action.update(start_time=action.start_time + relativedelta(days=-10),
                        update_time=action.update_time + relativedelta(days=-10)).apply()
    return True


def cal_time(start_time, end_time=None) -> [int, float]:
    if not end_time:
        end_time = time.time()
    else:
        end_time = time.mktime(end_time.timetuple())
    # debug模式下30秒就有一个步骤
    # t = (end_time - time.mktime(start_time.timetuple())) // 2
    t = (end_time - time.mktime(start_time.timetuple())) // 3600
    t2 = (end_time - time.mktime(start_time.timetuple())) % 3600 / 60
    return int(t), round(60-t2, 1)


def check_access(i, player):
    tmp_map: Map = get_world_data().get_map(i["name"])
    # bag = json.load(player.bag)
    if tmp_map.require_level > player.lv:
        return False
    return True


def get_random_pos(gmap: Map, player: PlayerDB):
    tmp = Stream(gmap.owned).filter(lambda i: check_access(i, player)).to_list()
    if len(tmp) == 0:
        return gmap
    total = Stream(tmp).map(lambda t: t["weight"]).sum()
    ran = random.uniform(0, total)
    t: float = 0
    for m in tmp:
        t += m["weight"]
        if t >= ran:
            return get_world_data().get_map(m["name"])
    return gmap


def get_random_item(gmap: Map):
    if len(gmap.mineral_list) == 0:
        return None
    tmp = gmap.mineral_list
    total = Stream(tmp).map(lambda t: t["weight"]).sum()
    ran = random.uniform(0, total)
    t: float = 0
    for i in gmap.mineral_list:
        t += i["weight"]
        if t >= ran:
            return get_world_data().get_item(i["name"]), i.get("num") or 1
    return None


def check_bag(cost, bag):
    for k, v in cost.items():
        if bag.get(k) is None:
            return False
        if bag.get(k) <= v:
            return False
    return True


def cost_bag(cost, bag):
    for k, v in cost.items():
        bag[k] -= v


async def cal_go_home(player: PlayerDB, adv: ActionDB):
    # 结算回家
    player.add_items(adv.item_get)
    await player.update(bag=player.bag, collection=player.collection).apply()
    await adv.delete()


# bool: True 已经回家了
async def adv_time_pass(event: GroupMessageEvent, force_go_home: bool = False) -> [str, bool]:
    uid = get_uid(event)
    # 第一步是计算角色行动了几次
    # 首先根据updateTime-createTime计算已经计算了几次行动
    # 然后根据now-createTime计算当前应该进行几次行动
    # 二者相减即是要更新的行动次数
    act: ActionDB = await ActionDB.get_action_by_uid(uid)
    if not act:
        return "你还没有出发呢！输入'出发'来出发吧", True
    player: PlayerDB = await PlayerDB.get_player_by_uid(uid)
    a, _ = cal_time(act.start_time, act.update_time)
    already_move = min(10, a)
    a, next_move_dif = cal_time(act.start_time)
    total_move = min(10, a)
    times = total_move - already_move

    should_go_home = True if total_move >= 10 else False
    log = act.log or ""
    flg = False

    # 角色即将获得的exp
    exp = 0
    pos = get_world_data().get_map(act.position)
    arrived = {pos: 1}  # 记录玩家到过的地方
    for i in range(20):
        if i >= times:
            if should_go_home:
                log += f"你觉得自己又累又渴，只能回来了！debug:{already_move} {total_move} {times}\n"
                break
            flg = True
            break
        # 检查去了哪里
        old_pos_name = pos.name
        pos = get_random_pos(pos, player)
        add_item(player.arrived, pos.name)
        if pos.name != old_pos_name:
            log += f"来到了{pos.name}...\n"
        # 检查消耗
        if not check_bag(pos.cost, player.bag):
            log += f"没有以下物品：{pos.cost}，没法坚持下去了\n"
            break
        cost_bag(pos.cost, player.bag)  # 消耗的物品在探险时就已经消耗
        # 检查收获
        item, num = get_random_item(pos)
        add_item(act.item_get, item.name, num)  # 添加的物品是放在暂存区的，需要结束探险时才能回来
        log += f"获得了{item.simple_name()}...\n"
        exp += item.lv
    async with db.transaction():
        # 计算完毕 增加获得的对应物品 记一下日志
        await act.update(item_get=act.item_get, log=log, position=pos.name, update_time=datetime.now()).apply()
        # 再去掉背包里的相关物品 更新exp和图鉴
        await player.update(bag=player.bag, dig_exp=player.dig_exp + exp, arrived=player.arrived).apply()
        if force_go_home or not flg:
            # 结算回家逻辑
            log += "你回家了！"
            await cal_go_home(player, act)
            return log, True
    if flg:
        return log + f"你还在外面，下一个步骤结算需要{next_move_dif}分钟，要强行回家的话请输入(强行回家)", False
    return log, flg
