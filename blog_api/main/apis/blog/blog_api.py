from flask import g, request
from flask_restful import Resource, abort, reqparse, fields, marshal
from flask_restful.fields import Raw, MarshallingException
from sqlalchemy import desc, text, or_
from sqlalchemy.exc import IntegrityError

from main.apis.admin.utils import verify_article
from main.apis.api_constant import USER
from main.apis.utils import login_required, get_now_time, handle_searched_content
from main.ext import cache, db
from main.models.blog.blog_model import BlogModel, BlogTypeModel, CommentModel, FavoriteModel
from main.models.user.user_model import UsersModel
from main.settings import SERVER_HOST

parse_blog = reqparse.RequestParser()
parse_blog.add_argument('token', type=str)
parse_blog.add_argument('type', type=str, required=True, help='请输入文章类型')
parse_blog.add_argument('title', type=str, required=True, help='请输入文章标题')
parse_blog.add_argument('content', type=str, required=True, help='请输入文章内容')
parse_blog.add_argument('is_private', type=bool, default=False)

parse_get_blog = reqparse.RequestParser()


class GetUsername(Raw):
    def format(self, value):
        try:
            user = UsersModel.query.get(value)
            if user.is_written_off:
                return '【已注销】'
            return user.username
        except Exception as e:
            raise MarshallingException(e)


class CommentsCount(Raw):
    def format(self, value):
        try:
            comments = CommentModel.query.filter_by(blog_id=value, is_verified=True).count()
            return comments
        except Exception as e:
            raise MarshallingException(e)


class LatestComment(Raw):
    def format(self, value):
        try:
            comment = CommentModel.query.filter_by(blog_id=value, is_verified=True).order_by(
                CommentModel.publish_time.desc()).first()
            if not comment:
                return None
            username = UsersModel.query.get(comment.user_id).username
            return {
                'username': username,
                'user_id': comment.user_id,
                'publish_time': str(comment.publish_time)
            }
        except Exception as e:
            raise MarshallingException(e)


blog_fields = {
    'type': fields.String,
    'title': fields.String,
    'content': fields.String,
    'user_id': fields.Integer,
    'publish_time': fields.DateTime('iso8601'),
    'update_time': fields.DateTime('iso8601'),
    'username': GetUsername(attribute='user_id')
}

blog_title_fields = {
    'id': fields.Integer,
    'type': fields.String,
    'title': fields.String,
    'user_id': fields.Integer,
    'username': GetUsername(attribute='user_id'),  # 返回user_id还是username？这是返回username
    'publish_time': fields.DateTime('iso8601'),
    'url': fields.Url('blog_api', absolute=True),
    'comments': CommentsCount(attribute='id'),  # 评论数
    'latest_comment': LatestComment(attribute='id')
}

all_blogs_title_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'data': fields.List(fields.Nested(blog_title_fields))
}


class BlogResource(Resource):
    """
    写新博客
    如果里面有敏感词，需要审核，is_verified改为False
    """

    def get(self, id):
        blog = BlogModel.query.get(id)
        token = request.args.get('token')
        if not blog:
            abort(404, error=f'未找到 id 为 {id} 的文章，可能您的输入有误或已被删除')
        if not blog.is_verified:
            abort(403, error='正在审核...')
        if blog.is_blocked:
            abort(403, error='此文章因为违规已被封禁')
        if blog.is_deleted:
            abort(403, error='此文章已被删除')
        if blog.is_private:
            if not token:
                abort(401, error='此为私密 blog ，你没有登录，无权访问')
            user_id = cache.get(token)
            if blog.user_id != user_id:
                abort(401, error='此为私密 blog ，你不是此 blog 的所有者，无权访问')

        data = marshal(blog, blog_fields)

        return data

    @login_required(USER)
    def put(self, id: int):
        """
        修改文章信息，修改文章时前端需要将文章所有内容加载后再对某一项进行修改，
        即使其中有一处或几处未修改，也是全局修改并提交。
        可修改的内容有 title、content、type、is_private 四个。(只改四个字段，也可以用patch方法实现)
        put 方法的实现前提是已执行了get获取到相关信息，并把这些信息放到待提交缓冲区
        :param id:文章的id
        :return: 序列化后的Json
        """
        args = parse_blog.parse_args()
        token = g.token
        type_ = args.get('type')
        title = args.get('title')
        content = args.get('content')
        is_private = args.get('is_private')
        user_id = cache.get(token)
        blog = BlogModel.query.get(id)
        if not blog:
            abort(404, error=f'未找到文章 id 为 {id} 的文章')
        if blog.user.id != user_id:
            abort(403, error='无权修改别人的文章')
        now = get_now_time()[1]
        blog.type = type_
        blog.title = title
        blog.content = content
        blog.update_time = now
        blog.is_private = is_private
        if not blog.save():
            abort(400, error='系统繁忙，请重试')
        data = {
            'msg': 'update ok',
            'data': {
                'type': type_,
                'title': title,
                'content': content,
                'update_time': str(now)
            }
        }
        return data, 201


class BlogsResource(Resource):
    """
    获取用户所有博客标题和回复内容，创建新博客
    """

    @login_required(USER)
    def get(self):
        args = parse_all.parse_args()
        page = args.get('page')
        page_size = 20
        user = g.user
        blogs = BlogModel.query.filter_by(user_id=user.id, is_deleted=False).order_by(text('-publish_time'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()

        data = {
            'msg': 'Got all articles of you.',
            'count': count,
            'data': blogs
        }

        return marshal(data, all_blogs_title_fields)

    @login_required(USER)
    def post(self):
        args = parse_blog.parse_args()
        user = g.user
        now_time = get_now_time()[0]
        last_blog = BlogModel.query.filter_by(user_id=user.id).order_by(desc(BlogModel.publish_time)).first()
        if last_blog:
            last_time = last_blog.publish_time
            if (now_time - last_time).seconds < 5 * 60:
                abort(403, error='发贴频繁，请等待5分钟后再发贴')

        type_ = args.get('type')
        title = args.get('title')
        content = args.get('content')
        is_private = args.get('is_private')

        blog_type = BlogTypeModel.query.get(type_)
        if not blog_type:
            abort(404, error=f'文章类型错误，请参考 {SERVER_HOST}types 中的类型')

        now = get_now_time()[1]
        blog = BlogModel()
        blog.type = type_
        blog.title = title
        blog.content = content
        blog.user_id = user.id
        blog.publish_time = now
        blog.ip = request.remote_addr
        blog.is_private = is_private
        blog.is_verified = verify_article(title, content)
        if not blog.save():
            abort(400, error='系统繁忙，请重试')
        data = {
            'msg': 'create ok',
            'data': {
                'url': f'http://{SERVER_HOST.split("/")[2]}/blog/{blog.id}',
                'type': type_,
                'title': title,
                'user': blog.user.username,
                'is_private': is_private,
                'publish_time': now,
                'is_verified': blog.is_verified
            }
        }

        return data, 201


class UserBlogResource(Resource):
    def get(self, id):
        args = parse_all.parse_args()
        page = args.get('page')
        page_size = 20
        blogs = BlogModel.query.filter_by(
            user_id=id, is_private=False, is_deleted=False, is_blocked=False
        ).order_by(text('-publish_time'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()
        data = {
            'msg': 'ok',
            'count': count,
            'data': blogs
        }

        return marshal(data, all_blogs_title_fields)


parse_all = reqparse.RequestParser()
parse_all.add_argument('page', type=int, default=1)


class AllArticlesResource(Resource):
    def get(self):
        """
        args里可传入多个筛选条件，默认查询全部未删除文章和已验证的文章，默认按时间排序。
        已注销的用户用户名统一显示为已注销。
        已封禁的用户文章也一同封禁(管理员在封禁用户时，文章就已经blocked)。
        :return:
        """
        args = parse_all.parse_args()
        page = args.get('page')
        page_size = 20
        blogs = BlogModel.query.filter_by(
            is_deleted=False, is_verified=True, is_blocked=False, is_private=False
        ).order_by(text('-publish_time'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()

        data = {
            'msg': 'Got all articles successful.',
            'count': count,
            'data': blogs
        }

        result = marshal(data, all_blogs_title_fields)

        return result


class Float(Raw):
    def format(self, value):
        comment = CommentModel.query.get(value)
        comments = CommentModel.query.filter_by(blog_id=comment.blog_id)
        return comments.all().index(comment) + 1


class CommentContent(Raw):
    def format(self, value):
        comment = CommentModel.query.get(value)
        if comment.is_blocked:
            return '已封禁'
        if comment.is_deleted:
            return '已删除'
        return comment.content


comment_fields = {
    'id': fields.Integer,
    'content': CommentContent(attribute='id'),
    'user_id': fields.Integer,
    'reply_id': fields.Integer,
    'blog_id': fields.Integer,
    'publish_time': fields.DateTime('iso8601'),
    'update_time': fields.DateTime('iso8601'),
    'author': GetUsername(attribute='user_id'),
    'float': Float(attribute='id')
}

comments_fields = {
    'msg': fields.String,
    'comments': fields.List(fields.Nested(comment_fields)),
    'count': fields.Integer
}

parse_comments = reqparse.RequestParser()
parse_comments.add_argument('blogID', type=int, required=True, help='请输入blogID')
parse_comments.add_argument('page', type=int, default=1)  # 第几页
parse_comments.add_argument('pageSize', type=int, default=10)  # 每页多少条评论

parse_add_comment = reqparse.RequestParser()
parse_add_comment.add_argument('blogID', type=int, required=True, help='请输入blogID')
parse_add_comment.add_argument('replyID', type=int, default=None)
parse_add_comment.add_argument('content', type=str, required=True, help='请输入评论内容')


class CommentsResource(Resource):
    def get(self):
        args = parse_comments.parse_args()
        blog_id = args.get('blogID')
        page = args.get('page')
        page_size = args.get('pageSize')

        all_comments = CommentModel.query.filter_by(blog_id=blog_id)
        count = all_comments.count()
        comments = all_comments.slice((page - 1) * page_size, page * page_size).all()
        data = {
            'msg': 'ok',
            'comments': comments,
            'count': count
        }
        result = marshal(data, comments_fields)

        return result

    @login_required(USER)
    def post(self):
        """
        增加评论
        """
        args = parse_add_comment.parse_args()
        blog_id = args.get('blogID')
        reply_id = args.get('replyID')
        content = args.get('content')
        user = g.user

        if len(content) < 5:
            abort(403, error='为减少无意义的回复，请确保你的评论大于5个字符')

        now = get_now_time()[1]
        comment = CommentModel()
        comment.user_id = user.id
        comment.content = content
        comment.publish_time = now
        comment.blog_id = blog_id
        comment.reply_id = reply_id
        comment.is_verified = verify_article(content=content)
        if not comment.save():
            abort(400, error='系统繁忙，请重试')

        return marshal(comment, comment_fields), 201


parse_put_comment = reqparse.RequestParser()
parse_put_comment.add_argument('content', type=str, required=True, help='请输入评论内容')


class CommentResource(Resource):
    @login_required(USER)
    def get(self, id):
        comment = CommentModel.query.get(id)
        if not comment:
            abort(404, error='未找到此评论')
        if comment.is_deleted:
            abort(404, error='此条评论已被删除')
        if comment.is_blocked:
            abort(400, error='此评论已被封禁')

        return marshal(comment, comment_fields)

    @login_required(USER)
    def put(self, id):
        args = parse_put_comment.parse_args()
        content = args.get('content')
        comment = CommentModel.query.get(id)
        if comment.is_deleted:
            abort(404, error='此条评论已被删除')
        comment.content = content
        if not comment.save():
            abort(400, error='系统繁忙，请重试')
        return marshal(comment, comment_fields), 201


class BlogTitle(Raw):
    def format(self, value):
        blog = BlogModel.query.get(value)
        return blog.title


user_comment_fields = {
    'id': fields.Integer,
    'content': fields.String,
    'user_id': fields.Integer,
    'reply_id': fields.Integer,
    'blog_id': fields.Integer,
    'publish_time': fields.DateTime('iso8601'),
    'update_time': fields.DateTime('iso8601'),
    'author': GetUsername(attribute='user_id'),
    'float': Float(attribute='id'),
    'blog_title': BlogTitle(attribute='blog_id')
}

user_comments_fields = {
    'msg': fields.String,
    'comments': fields.List(fields.Nested(user_comment_fields)),
    'count': fields.Integer
}

parse_my_comments = reqparse.RequestParser()
parse_my_comments.add_argument('page', type=int, default=1)


class UserCommentsResource(Resource):
    @login_required(USER)
    def get(self):
        page = parse_my_comments.parse_args().get('page')
        page_size = 10

        user = g.user
        comments = CommentModel.query.filter_by(user_id=user.id, is_deleted=False, is_blocked=False)
        count = comments.count()
        comments = comments.slice((page - 1) * page_size, page * page_size).all()
        data = {
            'msg': 'ok',
            'comments': comments,
            'count': count
        }
        return marshal(data, user_comments_fields)


class TypeBlogsResource(Resource):
    def get(self, id):
        """
        通过类型筛选blog
        """
        args = parse_all.parse_args()
        page = args.get('page')
        page_size = 20
        blogs = BlogModel.query.filter_by(
            type=str(id), is_deleted=False, is_verified=True, is_blocked=False, is_private=False
        ).order_by(text('-publish_time'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()
        data = {
            'msg': 'ok',
            'count': count,
            'data': blogs
        }

        return marshal(data, all_blogs_title_fields)


parse_favorite = reqparse.RequestParser()
parse_favorite.add_argument('blog_id', type=int, required=True, help='请输入要收藏的blogID')


class FavoriteResource(Resource):
    @login_required(USER)
    def get(self):
        user = g.user
        blog_id = parse_favorite.parse_args().get('blog_id')
        favorite = FavoriteModel.query.filter_by(blog_id=blog_id, user_id=user.id).first()
        if favorite:
            return {'favorite': True}
        return {'favorite': False}

    @login_required(USER)
    def post(self):
        user = g.user
        blog_id = parse_favorite.parse_args().get('blog_id')

        blog = BlogModel.query.get(blog_id)

        if blog.user_id == user.id:
            abort(400, error='不能收藏自己的 blog ')

        favorite = FavoriteModel(
            blog_id=blog_id,
            user_id=user.id
        )
        db.session.add(favorite)
        try:
            db.session.commit()
        except IntegrityError as e:
            err = str(e.orig)[1:-1].split(',', 1)
            print(err)
            if err[0] == '1452' and 'blog' in err[1]:
                abort(404, error=f'未找到此 blog_id({blog_id}) 对应的 blog')
            if err[0] == '1062':
                abort(400, error='您已收藏过此 blog 。')
            abort(400, error='系统繁忙')
        data = {
            'msg': 'ok',
            'data': {
                'blog_id': blog_id,
                'blog_title': blog.title,
            }
        }
        return data, 201

    @login_required(USER)
    def delete(self):
        user = g.user
        blog_id = parse_favorite.parse_args().get('blog_id')
        favorite = FavoriteModel.query.filter_by(blog_id=blog_id, user_id=user.id).first()
        if not favorite.delete():
            abort(400, error='系统繁忙，未能取消收藏，请重试')
        data = {
            'msg': 'ok',
            'data': {
                'blog_id': blog_id,
                'blog_title': BlogModel.query.get(blog_id).title,
            }
        }
        return data, 204


class MyFavoriteBlog(Resource):
    @login_required(USER)
    def get(self):
        args = parse_all.parse_args()
        page = args.get('page')
        page_size = 20
        user = g.user
        favorite_list = FavoriteModel.query.filter_by(user_id=user.id).all()
        blogs = BlogModel.query.filter(BlogModel.id.in_([i.blog_id for i in favorite_list])).order_by(
            text('-id'))
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()

        data = {
            'msg': 'Got all favorite blog of you.',
            'count': count,
            'data': blogs
        }

        return marshal(data, all_blogs_title_fields)


class SearchedContent(Raw):
    def format(self, value):
        pass


parse_search = reqparse.RequestParser()
parse_search.add_argument('word', type=str, required=True, help='搜索关键词不能为空')
parse_search.add_argument('page', type=int, default=1)


class SearchResource(Resource):
    def post(self):
        args = parse_search.parse_args()
        word = args.get('word')
        page = args.get('page')
        page_size = 20
        users = UsersModel.query.filter(UsersModel.username.like(f'%{word}%')).with_entities('id').all()
        user_ids = [i[0] for i in users]
        blogs = BlogModel.query.filter(
            or_(BlogModel.title.like(f'%{word}%'), BlogModel.user_id.in_(user_ids)),
            BlogModel.is_deleted == False,
            BlogModel.is_blocked == False,
            BlogModel.is_private == False,
            BlogModel.is_verified == True
        )
        count = blogs.count()
        blogs = blogs.slice((page - 1) * page_size, page * page_size).all()
        result = []
        for blog in blogs:
            item = {'id': blog.id, 'type': blog.type,
                    'title': blog.title.replace(word, f'<span class="keyWord">{word}</span>'),
                    'content': handle_searched_content(blog.content, word),
                    'user_id': blog.user_id,
                    'username': blog.user.username.replace(word, f'<span class="keyWord">{word}</span>'),
                    'publish_time': ' '.join(str(blog.publish_time).split('T')),
                    'url': f'{SERVER_HOST}blog/{blog.id}/'}
            result.append(item)
        print(result)

        data = {
            'msg': 'ok',
            'count': count,
            'data': result
        }

        return data
