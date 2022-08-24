import math
import random

from nonebot.adapters.onebot.v11 import GroupMessageEvent

from services import db
from .adv_handler import get_player_status
from .game_handler import Item, Mission
from .game_handler import get_world_data, Compose
from .mission_model import MissionDB
from .player_handler import get_player
from .player_model import PlayerDB
from .stream import Stream
from .utils import get_uid


def checker(player: PlayerDB, mission: Mission):
    if mission.repeatable != "一次":
        return False
    return True


async def get_available_mission(event) -> [list[Mission], str]:
    player: PlayerDB = await get_player(event)
    ms: dict[str, Mission] = get_world_data().get_mission_list()
    ms2: list[Mission] = Stream(ms.values()).filter(lambda m: checker(player, m)).to_list()
    tmp = '可领取任务列表:\n0: 我不做了\n'
    for i, j in enumerate(ms2):
        tmp += f'{i + 1}: {j.name}\n'
    return ms2, tmp


async def handle_receive_mission(event: GroupMessageEvent, mission: Mission):
    player: PlayerDB = await get_player(event)
    await MissionDB.receive_mission(player.name, get_uid(event), event.group_id, mission.name)
    return f"成功领取任务：{mission.name}\n" \
           f"{mission.des}\n\n" \
           f"任务目标：{mission.tar}\n" \
           f"任务提示：{mission.hint}\n"


async def get_submitable_mission(event: GroupMessageEvent):
    ms = await MissionDB.get_all_in_progress_mission(get_uid(event))
    tmp = '可提交任务列表:\n0: 我不提交了\n'
    for i, j in enumerate(ms):
        tmp += f'{i + 1}: {j.name}\n'
    return ms, tmp


def check_item(item, player):
    for i in item:
        if i["num"] > player.query_item(i["name"]):
            return False
    return True


def check_equip(equip, player):
    for i in equip:
        if not player.equip.get(i):
            return False
    return True


async def handle_submit_mission(event: GroupMessageEvent, ms: MissionDB):
    mission: Mission = get_world_data().get_mission(ms.name)
    player: PlayerDB = await get_player(event)
    # step1 根据时间更新任务事件的变化
    # 还没做
    # step2 检查任务类型
    if item := mission.check.get("check_item"):  # 具备型
        if check_item(item, player):
            return await handle_complete(event, mission, ms, player)
        else:
            return f"任务要求的物品你还没有完成！"

    if status := mission.check.get("player_status"):  # 状态型
        if await get_player_status(event) == status:
            return await handle_complete(event, mission, ms, player)
        else:
            return f"你还不处于{status}状态哦\n"

    if arrived := mission.check.get("player_arrived"):  # 经历型
        for ar in arrived:
            if player.arrived.get(ar) is None:
                return f"你还没去过{ar}呢！\n"
        return await handle_complete(event, mission, ms, player)

    if require_item := mission.check.get("require_item"):  # 索取型
        if check_item(require_item, player):
            player.cost_items(require_item)
            return await handle_complete(event, mission, ms, player)
        else:
            return f"任务要求的物品你还没有完成！"

    if equip := mission.check.get("check_equip"):  # 装备检查型
        if check_equip(equip, player):
            return await handle_complete(event, mission, ms, player)
        else:
            return f"任务要求的物品你还没有完成！"

    return "未知错误..."

    # step3 更新日志 反馈


async def handle_complete(event, mission, ms, player):
    async with db.transaction():
        await ms.update(status="已完成").apply()
        ans = f"任务【{mission.name}】完成\n"
        if len(mission.reward) != 0:
            reward_str = "获得奖励："
            for i in mission.reward.items():
                if i[0] == '升级':
                    player.lv = player.lv + 1
                    reward_str = f"升级到了{player.lv}!"
                else:
                    reward_str = f"获得 {i[0]} x{i[1]}\n"
                    player.add_items(mission.reward)
            await player.update(bag=player.bag, collection=player.collection, lv=player.lv).apply()
            ans += reward_str
        if next_str := mission.next:
            tmp = await handle_receive_mission(event, get_world_data().get_mission(next_str))
            ans += f"正在自动领取下一个任务...\n{tmp}"
        return ans


async def handle_look_mission(event: GroupMessageEvent, ms: MissionDB):
    mission: Mission = get_world_data().get_mission(ms.name)
    return f"{mission.name}\n" \
           f"{mission.des}\n\n" \
           f"任务目标：{mission.tar}\n" \
           f"任务提示：{mission.hint}\n"

