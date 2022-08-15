from extensive_plugin.mineral_stories.stream import Stream
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
    bag: dict[str, int] = db.Column(db.JSON(), nullable=False, default={'劳动点数': 100})
    # buff
    buff = db.Column(db.JSON(), nullable=False, default={})
    # 箱子
    box = db.Column(db.JSON(), nullable=False, default={})
    # 图鉴收集
    collection = db.Column(db.JSON(), nullable=False, default={})
    # 游历地点收集
    arrived = db.Column(db.JSON(), nullable=False, default={})
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

    # 注意 add完仍然需要update哦
    def add_item(self, name, cnt):
        from extensive_plugin.mineral_stories.utils import add_item
        add_item(self.bag, name, cnt)
        add_item(self.collection, name, cnt)

    def add_items(self, items):
        from extensive_plugin.mineral_stories.utils import add_items
        self.bag = add_items(self.bag, items)
        self.collection = add_items(self.collection, items)

    def showbag(self) -> str:
        if len(self.bag) != 0:
            return Stream(self.bag.items()).map(lambda i: f"{i[0]} x{i[1]}\n").reduce(lambda s1, s2: s1 + s2, '')
        return "没有任何物品"

    def show_equip(self) -> str:
        if len(self.equip) != 0:
            return Stream(self.equip.items()).map(lambda i: f"{i[0]}: {i[1]}\n").reduce(lambda s1, s2: s1 + s2, '')
        return "没穿任何装备"

    # 需要在外部检查物品数量是否足够
    def cost_item(self, item_name, num=1):
        if self.bag.get(item_name) >= num:
            self.bag[item_name] -= num
            if self.bag.get(item_name) == 0:
                self.bag.pop(item_name)
            return True
        else:
            logger.warning(f"使用{item_name}时发现物品不足")
            return False

    def query_item(self, item_name):
        return self.bag.get(item_name) or 0

    def get_bag(self) -> dict[str, int]:
        return self.bag

    def get_equip(self, _type) -> str:
        return self.equip.get(_type)

    def wear(self, _type, name):
        self.equip[_type] = name
        self.cost_item(name)

    def unwear(self, _type, name):
        from extensive_plugin.mineral_stories.utils import add_item
        # 这里的添加不会增加图鉴计数，所以不能直接调用playerDB.add_item
        add_item(self.bag, name, 1)
        self.equip.pop(_type)
