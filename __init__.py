import os
import platform

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText, ArgStr
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
import nonebot
from nonebot import Driver

from utils.message_builder import image
from .equip_handler import get_equip_list, handle_equip
from .forge_handler import get_forge_list, handle_forge, get_forge_num
from .look_handler import handle_look, show_info
from .mission_handler import get_available_mission, handle_receive_mission, get_submitable_mission, \
    handle_submit_mission, handle_look_mission
from .player_handler import register_new_player, get_player, get_user_status_str
from .adv_handler import get_user_status, adv_time_pass
from .game_handler import load_world_data, WorldInfo, Compose

__zx_plugin_name__ = "矿石物语"
__plugin_usage__ = """
usage：
    加入矿石物语：注册
    矿石商店：可以在这里购买火把，每个火把可以提供1小时的新手洞窟挖矿时间
    出发：前去洞窟挖矿
    冶炼：把挖到的矿拿去变成矿石！
    制作：把矿石和各种道具制作成装备
    我的背包：看看自己有哪些装备
""".strip()
__plugin_des__ = "属于我们的故事开始了！"
__plugin_type__ = ("群内小游戏",)
__plugin_cmd__ = ["挖矿"]
__plugin_version__ = 1.0
__plugin_author__ = "XiaoR"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": True,
    "cmd": ["挖矿"],
}
__plugin_configs__ = {
}

from .player_model import PlayerDB
from .shop_handler import get_store_list, buy_item_handle
from .use_handler import get_usable_item, use_item_handler

register = on_command("加入矿石物语", aliases={"注册矿石物语"}, priority=5, block=True)
set_out = on_command("出发", priority=5, block=True)
my_status = on_command("我的状态", priority=5, block=True)
go_home = on_command("回家", aliases={"归来", "探险状态"}, priority=5, block=True)
force_go_home = on_command("强行回家", aliases={"强制回家"}, priority=5, block=True)
game_store = on_command("矿石商店", aliases={"矿石物语商店", "劳动商店"}, priority=5, block=True)
use_item = on_command("使用", priority=5, block=False)
forge = on_command("制作", priority=5, block=True)
look_item = on_command("查看物品", aliases={"查询物品"}, priority=5, block=True)
equip_item = on_command("装备", priority=5, block=True)
receive_mission = on_command("领取任务", priority=5, block=True)
test = on_command("测试", priority=5, block=True)
submit_mission = on_command("提交任务", priority=5, block=True)
look_mission = on_command("查看任务", priority=5, block=True)

driver: Driver = nonebot.get_driver()


@driver.on_startup
async def events_read():
    await load_world_data()


# 注册部分
@register.handle()
async def handle_first_register(event: GroupMessageEvent):
    player = await get_player(event)
    if player:
        await register.reject(f"你已经有账号:{player.name} 了哦")


@register.got("name", prompt="你的角色名称是？（后面可以修改）")
async def handle_register_name(state: T_State, name: str = ArgStr("name")):
    if name.strip() == "":
        await register.reject("你输入的角色名字太短了！")
    if len(name) > 10:
        await register.reject("你输入的角色名字太长了！")
    await register.send(f"{name}")
    state["name"] = name


@register.got("yn", prompt="确认就叫这个了吗？(是/否)")
async def handle_register_yn(yn: str = ArgStr("yn")):
    if yn != "是":
        await register.finish("重新注册吧！")


@register.got("sex", prompt="你的性别是？(男/女)")
async def handle_register_sex(event: GroupMessageEvent, state: T_State, sex: str = ArgStr("sex")):
    if sex == "男" or sex == "女":
        await register.finish(await register_new_player(event, state["name"], sex))
    else:
        await register.reject("输错了，重新开始注册吧！")


# 出发历险
@set_out.handle()
async def _(state: T_State, event: GroupMessageEvent):
    player = await get_player(event)
    if not player:
        await set_out.finish("你还没有账号，请先输入'加入矿石物语'创建账号！")
    player, status, pos_list = await get_user_status(event)
    state["pos_list"] = pos_list
    state["player"] = player
    if status != "休息中":
        await set_out.finish(f"你正在{status}，不能再出发了")
    await set_out.send(user_status_to_str(player, pos_list))


@set_out.got("pos", prompt="你要去哪里？(数字)")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgStr("pos")):
    if not num.isdigit():
        await set_out.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num >= len(state["pos_list"]) or num < 0:
        await set_out.finish("输入的数字范围不对")
    pos = state["pos_list"][num]
    await adv_handler.go_outside(event, pos)
    await set_out.send(f"{state['player'].name}去{pos}了！")


@my_status.handle()
async def _(event: GroupMessageEvent):
    player = await get_player(event)
    if not player:
        await set_out.finish("你还没有账号，请先输入'加入矿石物语'创建账号！")
    await my_status.finish(await get_user_status_str(event))


def user_status_to_str(player: PlayerDB, pos_list: list[str]):
    tmp = ""
    for i, s in enumerate(pos_list):
        tmp += f"{i}: {s}\n"
    return f"""用户：{player.name}   探险等级：{player.lv}
可以去的地点：
{tmp}
"""


@go_home.handle()
async def _(event: GroupMessageEvent, state: T_State):
    player = await get_player(event)
    if not player:
        await set_out.finish("你还没有账号，请先输入'加入矿石物语'创建账号！")
    log, flg = await adv_time_pass(event)
    state["player_name"] = player.name
    if flg:
        await go_home.send(log)
    else:
        await go_home.finish(log)


@force_go_home.handle()
async def _(event: GroupMessageEvent):
    log, flg = await adv_time_pass(event, force_go_home=True)
    await force_go_home.finish(log)


@game_store.handle()
async def _(event: GroupMessageEvent, state: T_State):
    tmp, tmpstr = await get_store_list(event)
    await game_store.send(tmpstr)
    state["tmp"] = tmp


@game_store.got("choose", "需要买什么呢？(输入数字编号)")
async def _(event: GroupMessageEvent, state: T_State, p: str = ArgStr("choose")):
    if not p.isdigit():
        await game_store.finish("输入的格式不对，请输入数字")
    p = int(p)
    if p == 0:
        await game_store.finish("你离开了商店")
    if p > len(state["tmp"]) or p < 0:
        await game_store.finish("输入的数字范围不对")
    state["item"] = state["tmp"][p - 1]


@game_store.got("choose2", f"要买几个呢？(输入数量)")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgStr("choose2")):
    if not num.isdigit():
        await game_store.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num < 0:
        await game_store.finish("输入的格式不对，请输入正数")
    if num == 0:
        await game_store.finish("你离开了商店")

    await game_store.finish(await buy_item_handle(event, state["item"].name, state["item"].cost, num))


@use_item.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip() != "":  # 使用道具是官方商店的功能 使用才是游戏的功能 所以有任何参数都是 直接返回
        return
    item, tmp = await get_usable_item(event)
    state["item"] = item
    if len(item) == 0:
        await game_store.finish("没有可使用的物品")
    await game_store.send(tmp)


@use_item.got("choose", "需要使用什么呢？(输入数字编号)")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgStr("choose")):
    if not num.isdigit():
        await set_out.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num < 0 or num > len(state["item"]):
        await set_out.finish("输入的数字不在选定范围内")
    await use_item.finish(await use_item_handler(event, itemname=state["item"][num], itemcnt=1))


@forge.handle()
async def _(event: GroupMessageEvent, state: T_State):
    item, tmp = await get_forge_list(event)
    state["item"] = item
    await forge.send(tmp)


@forge.got("choose", "需要制作什么呢？(输入数字编号)")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgStr("choose")):
    if not num.isdigit():
        await forge.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num == 0:
        await forge.finish("好的")
    if num < 0 or num > len(state["item"]):
        await forge.finish("输入的数字不在选定范围内")
    can_forge_num = await get_forge_num(event, state["item"][num - 1])
    if can_forge_num <= 0:
        await forge.finish("你的素材不够制作")
    if can_forge_num == 1:
        await forge.finish(await handle_forge(event, state["item"][num - 1], 1))
    await forge.send(f"看起来最多可以做{can_forge_num}个")
    state["tar"] = state["item"][num - 1]
    state["tarnum"] = can_forge_num


@forge.got("choose2", "需要制作几个呢？(输入数字)")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgStr("choose2")):
    if not num.isdigit():
        await forge.finish("输入的格式不对，请输入数字")
    num = int(num)
    can_forge_num: int = state["tarnum"]
    tar: Compose = state["tar"]
    if num == 0:
        await forge.finish("你不做了")
    if num > can_forge_num:
        await forge.send(f"没法做那么多！帮你做{can_forge_num}个吧！")
        num = can_forge_num
    await forge.finish(await handle_forge(event, tar, num))


@look_item.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("name", args)


@look_item.got("name", prompt="请输入要查询物品的部分名称")
async def handle_city(event: GroupMessageEvent, state: T_State, item_name: str = ArgPlainText("name")):
    msg, flg, item = await handle_look(event, item_name)
    if flg:
        await look_item.finish(msg)
    else:
        state["item"] = item
        await look_item.send(msg)


@look_item.got("choose", prompt="请输入想查询的编号")
async def handle_city(state: T_State, event: GroupMessageEvent, num: str = ArgPlainText("choose")):
    if not num.isdigit():
        await set_out.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num < 0 or num > len(state["item"]):
        await set_out.finish("输入的数字不在选定范围内")
    await look_item.finish(await show_info(event, state["item"][num]))


@equip_item.handle()
async def _(event: GroupMessageEvent, state: T_State):
    tmp, tmpstr = await get_equip_list(event)
    if len(tmp) == 0:
        await equip_item.finish('你没有可用的装备')
    await equip_item.send(tmpstr)
    state['tmp'] = tmp


@equip_item.got("choose", prompt="请输入要装备物品的编号")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgPlainText("choose")):
    if not num.isdigit():
        await equip_item.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num == 0:
        return
    if num < 0 or num > len(state["tmp"]):
        await equip_item.finish("输入的数字不在选定范围内")
    await equip_item.finish(await handle_equip(event, state["tmp"][num - 1]))


@test.handle()
async def _():
    # await test.finish(Message.template('{}').format())
    return


@receive_mission.handle()
async def _(event: GroupMessageEvent, state: T_State):
    ms, msstr = await get_available_mission(event)
    await receive_mission.send(msstr)
    state["tmp"] = ms


@receive_mission.got("choose", prompt="请输入要领取的任务")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgPlainText("choose")):
    if not num.isdigit():
        await receive_mission.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num == 0:
        return
    if num < 0 or num > len(state["tmp"]):
        await receive_mission.finish("输入的数字不在选定范围内")
    await receive_mission.send(await handle_receive_mission(event, state["tmp"][num - 1]))


@submit_mission.handle()
async def _(event: GroupMessageEvent, state: T_State):
    ms, msstr = await get_submitable_mission(event)
    if len(ms) == 0:
        await submit_mission.finish("没有可提交的任务")
    await submit_mission.send(msstr)
    state["tmp"] = ms


@submit_mission.got("choose", prompt="请输入要提交的任务")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgPlainText("choose")):
    if not num.isdigit():
        await submit_mission.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num == 0:
        return
    if num < 0 or num > len(state["tmp"]):
        await submit_mission.finish("输入的数字不在选定范围内")
    await receive_mission.send(await handle_submit_mission(event, state["tmp"][num - 1]))


@look_mission.handle()
async def _(event: GroupMessageEvent, state: T_State):
    ms, msstr = await get_submitable_mission(event)
    if len(ms) == 0:
        await look_mission.finish("没有可查看的任务")
    await look_mission.send(msstr)
    state["tmp"] = ms


@look_mission.got("choose", prompt="请输入要查看的任务")
async def _(event: GroupMessageEvent, state: T_State, num: str = ArgPlainText("choose")):
    if not num.isdigit():
        await look_mission.finish("输入的格式不对，请输入数字")
    num = int(num)
    if num == 0:
        return
    if num < 0 or num > len(state["tmp"]):
        await look_mission.finish("输入的数字不在选定范围内")
    await look_mission.send(await handle_look_mission(event, state["tmp"][num - 1]))
# 挖矿 10小时 背包
# 制作 主道具 被动道具
# 解锁
# 交易
# 世界副本
# 图片
