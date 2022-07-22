import logging

from services.db_context import db
from datetime import datetime
from services.log import logger


class PlayerDB(db.Model):
    __tablename__ = "mineral_stories_player"

    id = db.Column(db.Integer(), primary_key=True)
    # 角色ID
    uid = db.Column(db.String(), nullable=False)
    # 角色名字
    name = db.Column(db.String(), nullable=False)
    # 探险家等级
    lv = db.Column(db.Integer(), nullable=False)
    # 性别
    sex = db.Column(db.String(), nullable=False)
    # 装备
    equip = db.Column(db.JSON(), nullable=False, default={})
    # 背包
    bag = db.Column(db.JSON(), nullable=False, default={})
    # buff
    buff = db.Column(db.JSON(), nullable=False, default={})
    # 箱子
    box = db.Column(db.JSON(), nullable=False, default={})
    # 出生时间
    create_time = db.Column(db.DateTime(), default=datetime.now)

    # 缺省字段
    reverse1 = db.Column(db.String(), nullable=True)
    reverse2 = db.Column(db.String(), nullable=True)
    reverse3 = db.Column(db.String(), nullable=True)

    @classmethod
    async def get_player_by_name(
            cls,
            name: str,
    ) -> "PlayerDB":
        try:
            async with db.transaction():
                return await PlayerDB.query.where(PlayerDB.name == name).gino.first()
        except Exception as e:
            logger.info(f"根据角色名字查询数据库出错 {type(e)}: {e}")

    @classmethod
    async def get_player_by_uid(
            cls,
            uid: str,
    ) -> "PlayerDB":
        try:
            async with db.transaction():
                return await PlayerDB.query.where(PlayerDB.uid == uid).gino.first()
        except Exception as e:
            logger.info(f"根据角色uid查询数据库出错 {type(e)}: {e}")

    @classmethod
    async def register(cls, uid: str, name: str, sex: str) -> "PlayerDB":
        try:
            async with db.transaction():
                logging.info(f"{name}加入游戏")
                return await cls.create(uid=uid, name=name, sex=sex, lv=1)
        except Exception as e:
            logger.info(f"新增角色出错 {type(e)}: {e}")
