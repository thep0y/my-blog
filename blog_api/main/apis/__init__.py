from flask_restful import Api

from main.apis.admin.admin_api import AdminLoginResource, AdminChangePassword, AdminGetResource
from main.apis.admin.blog_type_api import BlogTypeManage
from main.apis.admin.operation_api import AuditResource, GetAllNotVerifiedArticles, BlockResource, UnblockResource, \
    ManageComment
from main.apis.blog.blog_api import BlogResource, BlogsResource, AllArticlesResource, CommentsResource, CommentResource, \
    UserBlogResource, UserCommentsResource, TypeBlogsResource, FavoriteResource, MyFavoriteBlog, SearchResource
from main.apis.blog.file_api import UploadResource
from main.apis.user.user_api import UsersResource, VerifyCode, UserChangePassword, UserResetVerify, UserPasswordReset, \
    GetUsernameResource

api = Api()


def init_api(app):
    api.init_app(app)

# admin
api.add_resource(AdminLoginResource, '/admin/login', '/admin/login/')
api.add_resource(AdminChangePassword, '/admin/chpwd', '/admin/chpwd/')
api.add_resource(AuditResource, '/audit/<int:id>', '/audit/<int:id>/', endpoint='audit')
api.add_resource(BlockResource, '/block', '/block/', endpoint='block')
api.add_resource(UnblockResource, '/unblock', '/unblock/', endpoint='unblock')
api.add_resource(GetAllNotVerifiedArticles, '/ganvas')
api.add_resource(AdminGetResource, '/admin/get', '/admin/get/')
api.add_resource(BlogTypeManage, '/types', '/types/')
api.add_resource(ManageComment, '/manac/<int:id>', '/manac/<int:id>/')

# user & blog
api.add_resource(UsersResource, '/user', '/user/')
api.add_resource(UserBlogResource, '/user/<int:id>', '/user/<int:id>/')
api.add_resource(GetUsernameResource, '/getuser/<int:id>', '/getuser/<int:id>/')
api.add_resource(VerifyCode, '/verify/<arg>', '/verify/<arg>/')
api.add_resource(UserChangePassword, '/user/chpwd', '/user/chpwd/')
api.add_resource(UserResetVerify, '/user/resetverify', '/user/resetverify/')
api.add_resource(UserPasswordReset, '/user/reset', '/user/reset/')
api.add_resource(BlogResource, '/blog/<int:id>', '/blog/<int:id>/', endpoint='blog_api')
api.add_resource(TypeBlogsResource, '/blktype/<int:id>', '/blktype/<int:id>/')  # 类型下的blog，blogoftype的简写
api.add_resource(BlogsResource, '/blogs', '/blogs/')
api.add_resource(UploadResource, '/upload', '/upload/')
api.add_resource(FavoriteResource, '/favorite', '/favorite/')
api.add_resource(MyFavoriteBlog, '/myfav', '/myfav/')

# anyone
api.add_resource(AllArticlesResource, '/allarts')
api.add_resource(SearchResource, '/search', '/search/')

#commnets
api.add_resource(CommentsResource, '/comments')
api.add_resource(CommentResource, '/comment/<int:id>')
api.add_resource(UserCommentsResource, '/my-comments/')


