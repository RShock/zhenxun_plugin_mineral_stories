from services.db_context import db
from datetime import datetime
from services.log import logger


class PlayerDB(db.Model):
    __tablename__ = "mineral_stories_player"

    id: int = db.Column(db.Integer(), primary_key=True)
    # 角色ID
    uid: int = db.Column(db.String(), nullable=False)
    # 角色名字
    name: str = db.Column(db.String(), nullable=False)
    # 探险家等级
    lv: int = db.Column(db.Integer(), nullable=False)
    # 性别
    sex: str = db.Column(db.String(), nullable=False)
    # 挖掘经验
    dig_exp: int = db.Column(db.Integer(), default=0)
    # 锻造经验
    forge_exp = db.Column(db.Integer(), default=0)
    # 战斗经验
    battle_exp = db.Column(db.Integer(), default=0)
    # 装备
    equip = db.Column(db.JSON(), nullable=False, default={})
    # 背包
    bag = db.Column(db.JSON(), nullable=False, default={})
    # buff
    buff = db.Column(db.JSON(), nullable=False, default={})
    # 箱子
    box = db.Column(db.JSON(), nullable=False, default={})
    # 图鉴收集
    collection = db.Column(db.JSON(), nullable=False, default={})
    # 游历地点收集
    arrived = db.Column(db.JSON(), nullable=False, default={})
    # 当前金币情况
    gold = db.Column(db.Integer(), default=100)
    # 角色标签
    tag = db.Column(db.JSON(), nullable=False, default={})
    # 角色称号
    honor = db.Column(db.JSON(), nullable=False, default={})
    # 出生时间
    create_time = db.Column(db.DateTime(), default=datetime.now)
    # 来自群
    group_id = db.Column(db.BigInteger(), default=0)
    # 缺省字段
    reverse1 = db.Column(db.JSON(), nullable=True, default={})
    reverse2 = db.Column(db.JSON(), nullable=True, default={})
    reverse3 = db.Column(db.JSON(), nullable=True, default={})

    @classmethod
    async def get_player_by_name(
            cls,
            name: str,
    ) -> "PlayerDB":
        try:
            async with db.transaction():
                return await cls.query.where(cls.name == name).gino.first()
        except Exception as e:
            logger.info(f"根据角色名字查询数据库出错 {type(e)}: {e}")

    @classmethod
    async def get_player_by_uid(
            cls,
            uid: str,
    ) -> "PlayerDB":
        try:
            async with db.transaction():
                return await cls.query.where(cls.uid == uid).gino.first()
        except Exception as e:
            logger.info(f"根据角色uid查询数据库出错 {type(e)}: {e}")

    @classmethod
    async def register(cls, uid: str, group_id: int, name: str, sex: str) -> "PlayerDB":
        try:
            async with db.transaction():
                logger.info(f"{name}加入游戏")
                return await cls.create(uid=uid, name=name, sex=sex, lv=1, group_id=group_id)
        except Exception as e:
            logger.info(f"新增角色出错 {type(e)}: {e}")

    @classmethod
    async def set_status(cls, uid: str, status: str) -> None:
        try:
            async with db.transaction():
                s = await cls.get_player_by_uid(uid)
                await s.update(status=status).apply()
        except Exception as e:
            logger.info(f"设置角色状态出错 {type(e)}: {e}")
    #
    # @classmethod
    # async def update_bag(cls, uid: str, bag) -> None:
    #     try:
    #         async with db.transaction():
    #
    #     except Exception as e:
    #         logger.info(f"添加单个物品出错 {type(e)}: {e}")