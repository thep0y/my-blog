from main.ext import db
from main.models import UserBaseModel, Base


class AdminModel(UserBaseModel):
    """
    管理员模型，管理员账号只能管理，不能像普通用户一样发贴。
    如果 blog_api 规模大，可能需要许多的 admin 进行管理，这时就需要一个 super admin 账户管理这些 admin 账户
    """
    # is_super = db.Column(db.Boolean, default=False)  # blog_api 规模大时启动此字段，并增加Admin注册方法
    __tablename__ = 'admins'


class AdminOperationModel(Base):
    """
    管理员行为模型。
    用于记录管理员对于违规行为的处理和解封
    """
    __tablename__ = 'admin_operations'
    time = db.Column(db.DateTime)
    operation = db.Column(db.Integer, nullable=False)
    target_id = db.Column(db.String(32), nullable=False)
    reason = db.Column(db.Integer)
