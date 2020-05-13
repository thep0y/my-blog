from main.ext import db
from main.models import UserBaseModel, Base


class UsersModel(UserBaseModel):
    """
    用户模型
    """
    __tablename__ = 'users'
    email = db.Column(db.String(40), nullable=False, unique=True)
    phone = db.Column(db.BigInteger, unique=True)
    register_time = db.Column(db.DateTime, nullable=False)
    register_ip = db.Column(db.String(15), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # 验证
    is_written_off = db.Column(db.Boolean, default=False)  # 注销/删除
    is_blocked = db.Column(db.Integer, default=False)  # 封禁


class UserLoginRecordModel(Base):
    """
    用户访问记录
    """
    __tablename__ = 'user_login_record'
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    time = db.Column(db.DateTime)


class BlockedUserModel(Base):
    __tablename__ = 'blocked_users'
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), nullable=False)
    reason = db.Column(db.String(40), nullable=False)

