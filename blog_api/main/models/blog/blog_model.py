from main.ext import db
from main.models import Base
from main.models.user.user_model import UsersModel


class BlogTypeModel(Base):
    """
    博客类型，只有管理员才能增删改
    """
    __tablename__ = 'blog_types'
    type = db.Column(db.String(15), nullable=False, unique=True)


class BlogModel(Base):
    """
    博客正文
    """
    __tablename__ = 'blogs'
    type = db.Column(db.String(10), nullable=False)  # 一篇文章的类型可能有重合，多类型应存储为"[1,2,3]"格式，但无法使用外键。本Blog只支持一个类型。
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, nullable=False)
    update_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), nullable=False)
    is_verified = db.Column(db.Boolean, default=True)  # 默认发贴不需要审核，但内容里有敏感字的需要审核
    is_deleted = db.Column(db.Boolean, default=False)  # 默认不删除
    is_blocked = db.Column(db.Boolean, default=False)  # 默认不封禁
    is_top = db.Column(db.Boolean, default=False)  # 默认不置顶
    is_private = db.Column(db.Boolean, default=False)  # 默认非私人文章
    ip = db.Column(db.String(15), nullable=False)  # 发贴时的ip地址，为判断用户是否因盗号发违规贴
    user = db.relationship('UsersModel', backref='user')


class CommentModel(Base):
    """
    博客评论
    """
    __tablename__ = 'comments'
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, nullable=False)
    update_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)  # 评论也不能直接删除，可作为证据
    is_verified = db.Column(db.Boolean, default=True)  # 默认发贴不需要审核，但内容里有敏感字的需要审核
    is_blocked = db.Column(db.Boolean, default=False)  # 用户被封，其评论也被封，默认不封
    blog_id = db.Column(db.Integer, db.ForeignKey(BlogModel.id))
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id))
    reply_id = db.Column(db.Integer)  # 回复第几个评论
    user = db.relationship('UsersModel', backref='users')
    blog = db.relationship('BlogModel', backref='blog')


class BlockedBlogModel(Base):
    """
    封禁blog
    """
    __tablename__ = 'blocked_blogs'
    blog_id = db.Column(db.Integer, db.ForeignKey(BlogModel.id), nullable=False)
    reason = db.Column(db.String(40), nullable=False)
    blog = db.relationship('BlogModel', backref='blogs')


class DeletedBlogModel(BlockedBlogModel):
    """
    删除blog
    """
    __tablename__ = 'deleted_blogs'


class BlockedIPModel(Base):
    """
    封禁ip
    """
    __tablename__ = 'blocked_IPs'
    ip = db.Column(db.String(15), nullable=False)  # 同一ip多个账号多次发布违规内容就封禁此ip
    reason = db.Column(db.String(40), nullable=False)


class FavoriteModel(Base):
    """
    收藏的blog
    """
    __tablename__ = 'favorite'
    blog_id = db.Column(db.Integer, db.ForeignKey(BlogModel.id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), nullable=False)
    __table_args__ = (db.UniqueConstraint(blog_id, user_id, name='idx_blog_user'),)  # 添加联合唯一约束
