import os

from nonebot.adapters.onebot.v11 import MessageSegment


def add_items(a, b) -> dict[str, int]:
    temp = dict()
    for key in a.keys() | b.keys():
        temp[key] = sum([d.get(key, 0) for d in (a, b)])
    return temp


def add_item(dic, name, cnt):
    if dic.get(name) is None:
        dic[name] = cnt
    else:
        dic[name] += cnt


game_path = os.path.dirname(__file__)


# 不知道官方的那个image怎么用 只能直接用自己文件下的的resources+MessageSegment了 会用的可以告诉我
def get_image(name):
    image_file = f"file:///{game_path}/resources/image/item/{name}.png"
    return MessageSegment.image(image_file)


def get_uid(event) -> str:
    return str(event.user_id)
