import platform

from nonebot import on_command

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

set_out = on_command("挖矿", aliases={"出发"}, priority=5, block=True)


@set_out.handle()
async def _():
    await set_out.finish("你出发了！")