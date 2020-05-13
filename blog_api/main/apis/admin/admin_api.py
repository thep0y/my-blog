from flask_restful import fields, Resource, reqparse, abort

from main.apis.admin import parser_base
from main.apis.api_constant import HTTP_OK, ADMIN, HTTP_NOT_ALLOWED_METHOD, HTTP_NOT_AUTHENTICATION, HTTP_FORBIDDEN
from main.apis.utils import generate_admin_token, login_required, clear_other_login_caches, \
    verify_user_password, get_logined_user
from main.ext import cache
from main.models.admin.admin_model import AdminModel

admin_fields = {
    'username': fields.String,
    'password': fields.String(attribute='_password')
}

single_admin_fields = {
    'data': fields.Nested(admin_fields),
    'status': fields.Integer,
    'msg': fields.String
}

parser = parser_base.copy()
parser.remove_argument('action')


class AdminLoginResource(Resource):
    def get(self):
        abort(HTTP_NOT_ALLOWED_METHOD, error='登录请用 POST 请求方式')

    def post(self):
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')

        user = verify_user_password(ADMIN, username, password)

        token = generate_admin_token()
        cache.set(token, user.id, timeout=60 * 60 * 24)

        data = {
            'msg': '已登录管理员账户',
            'token': token
        }
        return data, HTTP_OK


parse_change_pwd = reqparse.RequestParser()
parse_change_pwd.add_argument('token', required=True, type=str, help='请输入token')
parse_change_pwd.add_argument('old', required=True, type=str, help='请输入你的原密码')
parse_change_pwd.add_argument('new', required=True, type=str, help='请输入你的新密码')


class AdminChangePassword(Resource):
    """
    修改密码，admin只支持修改密码，不能重置密码
    """

    def get(self):
        abort(403, error='当前 url 仅支持 POST 方法访问')

    @login_required(ADMIN)
    def post(self):
        args = parse_change_pwd.parse_args()
        token = args.get('token')
        user_id = cache.get(token)
        if not user_id:
            abort(401, error='未登录或登录过期，请重新登录')
        old = args.get('old')
        new = args.get('new')

        user = AdminModel.query.get(user_id)
        if not user:
            abort(401, error='用户不存在或已注销')
        if not user.check_password(old):
            abort(401, error='原密码不正确')

        user.password = new

        if not user.save():
            abort(400, error='密码修改失败，请重试')

        # 修改密码后，清除缓存中所有与当前用户关联的缓存
        clear_other_login_caches(ADMIN, user_id)

        data = {
            'msg': 'change password successful',
        }

        return data


parser_get = reqparse.RequestParser()
parser_get.add_argument('token', type=str, required=True, help='请输入管理员token')


class AdminGetResource(Resource):
    def post(self):
        args = parser_get.parse_args()
        token = args.get('token')
        user, user_id = get_logined_user(ADMIN, token)
        data = {
            'id': user_id,
            'username': user.username,
        }

        return data, HTTP_OK
