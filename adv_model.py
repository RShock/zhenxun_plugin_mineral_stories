from services.db_context import db
from datetime import datetime


class StockDB(db.Model):
    __tablename__ = "mineral_stories_adventure"

    id = db.Column(db.Integer(), primary_key=True)
    # 角色ID
    uid = db.Column(db.String(), nullable=False)
    # 在哪里
    position = db.Column(db.String(), nullable=False)
    # 什么时候去的
    start_time = db.Column(db.DateTime(), default=datetime.now)
    # 缺省字段
    reverse1 = db.Column(db.String(), nullable=False)
    reverse2 = db.Column(db.String(), nullable=False)
    reverse3 = db.Column(db.String(), nullable=False)

