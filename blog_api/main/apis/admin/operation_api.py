from flask_restful import Resource, fields, marshal, abort, reqparse
from flask_restful.fields import Raw, MarshallingException
from sqlalchemy import text

from main.apis.api_constant import ADMIN, ADMIN_MANAGE_USER, ADMIN_MANAGE_BLOG, ADMIN_MANAGE_IP
from main.apis.utils import login_required
from main.ext import db
from main.models.blog.blog_model import BlogModel, CommentModel, BlockedBlogModel, BlockedIPModel
from main.models.user.user_model import UsersModel, BlockedUserModel

not_verified_article_fields = {
    'id': fields.Integer,
    'type': fields.String,
    'title': fields.String,
    'publish_time': fields.DateTime('iso8601'),
    'url': fields.Url('audit', absolute=True)
}

all_not_verified_articles_fields = {
    'msg': fields.String,
    'data': fields.List(fields.Nested(not_verified_article_fields)),
    'count': fields.Integer
}

parse_not_verified_blog = reqparse.RequestParser()
parse_not_verified_blog.add_argument('page', type=int, default=1)  # 第几页


class GetAllNotVerifiedArticles(Resource):
    """
    获取所有需验证的文章
    """

    @login_required(ADMIN)  # TODO 分页
    def get(self):
        args = parse_not_verified_blog.parse_args()
        page = args.get('page')
        page_size = 20  # 每页的数量
        print(page)
        blogs = BlogModel.query.filter_by(is_verified=False, is_blocked=False, is_deleted=False).order_by(
            text('-publish_time'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()

        data = {
            'msg': 'Got all not verified articles',
            'data': blogs,
            'count': count
        }

        return marshal(data, all_not_verified_articles_fields)


class GetUsername(Raw):
    def format(self, value):
        try:
            user = UsersModel.query.get(value)
            return user.username
        except Exception as e:
            raise MarshallingException(e)


audit_blog_fields = {
    'id': fields.Integer,
    'type': fields.String,
    'title': fields.String,
    'content': fields.String,
    'publish_time': fields.DateTime('iso8601'),
    'user_id': fields.Integer,
    'username': GetUsername(attribute='user_id')
}

parse_delete = reqparse.RequestParser()
parse_delete.add_argument('verified', type=bool, default=False)
parse_delete.add_argument('deleted', type=bool, default=False)
parse_delete.add_argument('reason', type=str)


class AuditResource(Resource):
    """
    审核文章
    """

    @login_required(ADMIN)
    def get(self, id):

        blog = BlogModel.query.get(id)
        if blog.is_deleted:
            abort(400, error='此 blog 已被删除，请在已删除里查看此 blog。')
        if blog.is_verified:
            abort(400, error='此文章已通过验证')
        if not blog:
            abort(404, error=f'未找到 id 为 {id} 的文章')
        data = {
            'msg': 'ok',
            'data': marshal(blog, audit_blog_fields)
        }

        return data

    @login_required(ADMIN)
    def post(self, id):
        """
        提交审核结果，审核不通过的文章直接封禁并删除
        """
        args = parse_delete.parse_args()
        deleted = args.get('deleted')
        verified = args.get('verified')
        reason = args.get('reason')
        blog = BlogModel.query.get(id)
        if not blog:
            abort(404, error=f'未找到 id 为 {id} 的文章')
        if blog.is_deleted:
            abort(404, error='文章已被删除')
        if blog.is_verified and verified:
            abort(403, error='此blog已通过审核，无需再次审核')
        if deleted and verified:
            abort(400, error='错误的操作')
        if not deleted and not verified:
            abort(400, error='未更改 blog 状态')
        if verified:
            blog.is_verified = True
            db.session.commit()
            data = {
                'msg': 'The blog_api is verified successful.',
                'data': marshal(blog, audit_blog_fields)
            }

            return data
        if deleted:
            blog.is_deleted = deleted
            if not reason:
                abort(400, reason='If `verified` is False and `deleted` is True, the reason can not be None.')
            blog.is_blocked = True

            blocked_blog = BlockedBlogModel(blog_id=id, reason=reason)
            db.session.add(blocked_blog)
            db.session.commit()

            data = {
                'msg': 'The blog has been deleted due to violation of regulations.',
                'data': marshal(blog, audit_blog_fields)
            }
            return data


class DelBlogResource(Resource):
    """
    彻底删除文章，删除行为不可恢复
    """
    pass


parse_block = reqparse.RequestParser()
parse_block.add_argument('action', type=str, required=True, help='请输入请求参数')

parse_unblock_user = parse_block.copy()
parse_unblock_user.add_argument('id', type=int, required=True, help='请输入用户id')

parse_block_user = parse_unblock_user.copy()
parse_block_user.add_argument('reason', type=str, required=True, help='请输入封禁用户的原因')

parse_unblock_blog = parse_block.copy()
parse_unblock_blog.add_argument('id', type=int, required=True, help='请输入文章id')

parse_block_blog = parse_unblock_blog.copy()
parse_block_blog.add_argument('reason', type=str, required=True, help='请输入封禁文章的原因')

parse_unblock_ip = parse_block.copy()
parse_unblock_ip.add_argument('ip', type=str, required=True, help='请输入文章ip')

parse_block_ip = parse_unblock_ip.copy()
parse_block_ip.add_argument('reason', type=str, required=True, help='请输入封禁ip的原因')


class BlockResource(Resource):
    """
    封禁用户、文章
    """

    @login_required(ADMIN)
    def post(self):
        args = parse_block.parse_args()
        action = args.get('action')
        if action == ADMIN_MANAGE_USER:
            args = parse_block_user.parse_args()
            id_ = args.get('id')
            reason = args.get('reason')
            user = UsersModel.query.get(id_)
            if not user:
                abort(404, error='未找到此用户')
            if user.is_blocked:
                abort(403, error='此用户已被封禁')
            user.is_blocked = True

            blogs = BlogModel.query.filter_by(user_id=id_).all()
            if blogs:
                for blog in blogs:
                    blog.is_blocked = True

            comments = CommentModel.query.filter_by(user_id=id_).all()
            if comments:
                for comment in comments:
                    comment.is_blocked = True

            blocked_user = BlockedUserModel()
            blocked_user.user_id = id_
            blocked_user.reason = reason
            db.session.add(blocked_user)

            db.session.commit()

            data = {
                'msg': f'{user.username} 与其文章已被封禁'
            }

            return data, 200
        elif action == ADMIN_MANAGE_BLOG:
            args = parse_block_blog.parse_args()
            id_ = args.get('id')
            reason = args.get('reason')
            blog = BlogModel.query.get(id_)
            if not blog:
                abort(404, error='未找到此 blog_api')
            if blog.is_blocked:
                abort(403, error='此blog已被封禁')
            blog.is_blocked = True
            blocked_blog = BlockedBlogModel(blog_id=id_, reason=reason)
            db.session.add(blocked_blog)
            db.session.commit()
            data = {
                'msg': f'The blog_api(id={id_}) has been blocked.'
            }

            return data
        elif action.lower() == ADMIN_MANAGE_IP.lower():
            args = parse_block_ip.parse_args()
            ip = args.get('ip')
            reason = args.get('reason')
            ip_ = BlockedIPModel.query.filter_by(ip=ip).first()
            if ip_:
                abort(403, error='此ip已被封禁')
            blocked_ip = BlockedIPModel()
            blocked_ip.ip = ip
            blocked_ip.reason = reason
            if not blocked_ip.save():
                abort(400, error='系统繁忙，请稍后再试')

            data = {
                'msg': f'The ip[`{ip}`] has been blocked successful.'
            }

            return data
        else:
            abort(404, error='请求参数错误')


class UnblockResource(Resource):
    def post(self):
        args = parse_block.parse_args()
        action = args.get('action')

        if action == ADMIN_MANAGE_USER:
            args = parse_unblock_user.parse_args()
            id_ = args.get('id')
            user = UsersModel.query.get(id_)
            if not user:
                abort(404, error='未找到此用户')
            if not user.is_blocked:
                abort(403, error='此用户未被封禁')
            user.is_blocked = False
            blogs = BlogModel.query.filter_by(user_id=id_).all()
            if blogs:
                for blog in blogs:
                    blog.is_blocked = False
            comments = CommentModel.query.filter_by(user_id=id_).all()
            if comments:
                for comment in comments:
                    comment.is_blocked = False
            db.session.commit()

            data = {
                'msg': f'{user.username} 与其文章已解封'
            }

            return data, 200
        elif action == ADMIN_MANAGE_BLOG:
            args = parse_unblock_blog.parse_args()
            id_ = args.get('id')
            blog = BlogModel.query.get(id_)
            if not blog:
                abort(404, error='未找到此 blog')
            if not blog.is_blocked:
                abort(403, error='此blog并未被封禁')
            blog.is_blocked = False

            blocked_blog = BlockedBlogModel.query.filter_by(blog_id=id_).first()
            db.session.delete(blocked_blog)

            db.session.commit()

            data = {
                'msg': f'The blog(id={id}) has been unblocked.'
            }

            return data
        else:
            abort(404, error='请求参数错误')


class ManageComment(Resource):
    @login_required(ADMIN)
    def post(self, id):
        comment = CommentModel.query.get(id)
        if not comment:
            abort(404, error='评论不存在')
        if comment.is_deleted:
            abort(400, error='评论已被删除')
        if comment.is_blocked:
            abort(400, error='评论已被封禁')

        comment.is_blocked = True
        db.session.commit()

        data = {
            'id': id,
            'msg': '评论已封禁'
        }

        return data

    @login_required(ADMIN)
    def delete(self, id):
        comment = CommentModel.query.get(id)
        if not comment:
            abort(404, error='评论不存在')
        if comment.is_deleted:
            abort(400, error='评论已被删除')

        comment.is_deleted = True
        db.session.commit()

        data = {
            'id': id,
            'msg': '评论已删除'
        }

        return data
