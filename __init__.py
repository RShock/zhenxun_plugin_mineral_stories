import platform

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText, ArgStr
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from .player_handler import register_new_player, check_register

__zx_plugin_name__ = "矿石物语"
__plugin_usage__ = """
usage：
    属于我们的故事开始了！
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

register = on_command("加入矿石物语", priority=5, block=True, )
set_out = on_command("挖矿", aliases={"出发"}, priority=5, block=True)


@set_out.handle()
async def _():
    await set_out.finish("你出发了！")


@register.handle()
async def handle_first_register(event: GroupMessageEvent):
    player = await check_register(event)
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
async def handle_register_name(yn: str = ArgStr("yn")):
    if yn != "是":
        await register.finish("重新注册吧！")


@register.got("sex", prompt="你的性别是？(男/女)")
async def handle_register_name(event: GroupMessageEvent, state: T_State, sex: str = ArgStr("sex")):
    if sex == "男" or sex == "女":
        await register.finish(await register_new_player(event, state["name"], sex))
    else:
        await register.reject("输错了，重新开始注册吧！")

# 挖矿 10小时 背包
# 制作 主道具 被动道具
# 解锁
# 交易
# 世界副本
# 图片
