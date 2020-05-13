import random
import time

from flask import request, redirect, g
from flask_restful import Resource, fields, reqparse, abort, marshal

from main.apis.api_constant import HTTP_OK, USER_ACTION_REGISTER, HTTP_CREATE_OK, USER_ACTION_LOGIN, USER_ACTION_VERIFY, \
    USER_ACTION_LOGOUT, USER, USER_ACTION_WRITTEN_OFF, HTTP_FORBIDDEN, HTTP_ERROR, USER_ACTION_GET_INFO, \
    HTTP_NOT_AUTHENTICATION
from main.apis.user.utils import send_mail
from main.apis.utils import check_user_exits, generate_user_token, \
    get_ordinary_user, check_email, clear_other_login_caches, get_now_time, generate_jwt_token, parse_jwt_token, \
    get_logined_user, send_verify_code_by_mail, login_required, generate_verify_token, verify_user_password
from main.ext import cache
from main.models.user.user_model import UsersModel, UserLoginRecordModel

good_fields = {
    'name': fields.String(attribute='g_name'),
    'price': fields.Float(attribute='g_price'),
    'count': fields.Integer(attribute='g_count'),
}

good_status_fields = {
    'data': fields.Nested(good_fields),
    'status': fields.Integer,
    'msg': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument('action', type=str, required=True, help='请输入请求参数')

parser_register = parser.copy()
parser_register.add_argument('username', type=str, required=True, help='请输入用户名')
parser_register.add_argument('password', type=str, required=True, help='请输入密码')
parser_register.add_argument('email', type=str, required=True, help='请输入邮箱')
parser_register.add_argument('phone', type=int, required=True, help='请输入手机号')

parser_login = parser.copy()
parser_login.add_argument('username', type=str, required=True, help='请输入用户名、邮箱或手机号')
parser_login.add_argument('password', type=str, required=True, help='请输入密码')

parser_verify = parser.copy()
parser_verify.add_argument('token', type=str, required=True, help='请输入要验证用户的token')

parser_get = parser_verify.copy()

parser_verify_code = parser.copy()

parser_logout = parser_verify.copy()
parser_logout.remove_argument('action')

parser_patch = reqparse.RequestParser()
parser_patch.add_argument('email', type=str)
parser_patch.add_argument('phone', type=int)
parser_patch.add_argument('email_verify_code', type=int)
parser_patch.add_argument('phone_verify_code', type=int)

parse_change_pwd = reqparse.RequestParser()
parse_change_pwd.add_argument('token', required=True, type=str, help='请输入token')
parse_change_pwd.add_argument('old', required=True, type=str, help='请输入你的原密码')
parse_change_pwd.add_argument('new', required=True, type=str, help='请输入你的新密码')  # 只需要输入一个新密码，确认密码通过前端完成

parse_reset_verify = reqparse.RequestParser()
parse_reset_verify.add_argument('email', required=True, type=str, help='请输入你注册的邮箱')
parse_reset_verify.add_argument('verify_code', required=True, type=int, help='请输入你邮箱收到的验证码')

parse_reset_pwd = reqparse.RequestParser()
parse_reset_pwd.add_argument('token', required=True, help='请输入token')
parse_reset_pwd.add_argument('new', required=True, help='请输入新密码')  # 前端重复确认

user_fields = {
    'username': fields.String,
    'email': fields.String,
}

single_user_data_fields = {
    'data': fields.Nested(user_fields),
    'status': fields.Integer,
    'msg': fields.String
}


class UsersResource(Resource):
    def get(self):
        args = parser.parse_args()
        action = args.get('action').lower()
        if action == USER_ACTION_VERIFY:
            args = parser_verify.parse_args()
            token = args.get('token')
            payload = parse_jwt_token(token)
            if not payload:
                abort(400, error='验证失败，请重新发送验证邮件')
            send_time = payload['iat']
            user_id = payload['user_id']

            now_time = int(time.time())

            if now_time - send_time > 5 * 60:
                abort(400, error='此验证链接已失效，请发送新的验证邮件')

            user = get_ordinary_user(int(user_id))
            if not user:
                abort(404, error='账户没有注册成功，请重新注册')
            if user.is_verified:
                abort(400, msg='您的邮箱已验证，请勿重复验证')
            user.is_verified = True
            if not user.save():
                abort(400, error='验证失败，请重新发送验证邮件进行验证')
            return redirect('http://39.97.78.47/verified/')
        elif action == USER_ACTION_REGISTER:
            abort(400, error='register 只能用 POST 方法访问')
        elif action == USER_ACTION_LOGIN:
            abort(400, error='login 只能用 POST 方法访问')
        else:
            abort(404, error='非法的请求参数')

    def post(self):
        args = parser.parse_args()
        action = args.get('action').lower()
        if action == USER_ACTION_REGISTER:
            args = parser_register.parse_args()
            username = args.get('username')
            email = args.get('email')
            phone = args.get('phone')
            if not check_email(email):
                abort(403, error='邮箱格式错误，非正确邮箱将无法注册')
            password = args.get('password')
            check_user_exits(username, email, phone)

            now_time = get_now_time()
            user = UsersModel()
            user.username = username
            user.email = email
            user.phone = phone
            user.password = password
            user.register_time = now_time[1]
            user.register_ip = request.remote_addr
            if not user.save():
                abort(400, error='创建失败')

            token = generate_jwt_token(user.id)
            # celery发送验证邮件
            send_mail.delay(email, token)

            data = {
                'status': HTTP_CREATE_OK,
                'msg': '创建成功，已向您的邮箱发送了一封验证邮件，请及时验证',
                'data': user
            }

            return marshal(data, single_user_data_fields), HTTP_CREATE_OK  # 将要返回的状态码直接以数字作为return元组的第2个元素
        elif action == USER_ACTION_LOGIN:
            args_login = parser_login.parse_args()
            username_or_email = args_login.get('username')
            password = args_login.get('password')

            user = verify_user_password(USER, username_or_email, password)

            if not user.is_verified:
                token = generate_jwt_token(user.id)
                send_mail.delay(user.email, token)
                abort(HTTP_FORBIDDEN, error='您的邮箱尚未验证，现已发送验证邮件，请及时验证。')

            # 记录用户登录信息
            record = UserLoginRecordModel()
            record.user_id = user.id
            record.ip = request.remote_addr
            record.time = get_now_time()[1]
            if not record.save():
                abort(HTTP_ERROR, error='系统繁忙，请稍后重试')

            # 清除缓存中当前用户之前生成的登录token
            clear_other_login_caches(USER, user.id)
            # 生成用户登陆token放在cache里
            token = generate_user_token()
            cache.set(token, user.id, timeout=60 * 60 * 24 * 30)

            data = {
                'msg': '已登录',
                'token': token
            }
            return data, HTTP_OK
        elif action == USER_ACTION_LOGOUT:
            args = parser_logout.parse_args()
            token = args.get('token')
            user_id = cache.get(token)
            if not user_id:
                abort(400, error='此用户已退出登录')
            user = UsersModel.query.get(user_id)
            if not user:
                abort(400, error=f'id为 -> {user_id} 的账号不存在或已被删除')
            cache.delete(token)

            data = {
                'status': HTTP_OK,
                'msg': f'用户 -> {user.username} 已退出登录'
            }

            return data
        elif action == USER_ACTION_WRITTEN_OFF:
            return
        elif action == USER_ACTION_GET_INFO:
            args = parser_get.parse_args()
            token = args.get('token')
            user, user_id = get_logined_user(USER, token)
            data = {
                'id': user_id,
                'username': user.username,
            }

            return data, HTTP_OK
        else:
            abort(404, error='非法的请求参数')

    @login_required(USER)
    def patch(self):
        """
        只允许修改邮箱、手机号、性别、生日等个人资料，本blog只有邮箱和手机号
        如果修改邮箱或手机号，需要重新验证，否则用户状态重置到未验证
        :return:
        """
        args = parser_patch.parse_args()
        print(args)
        email = args.get('email')
        phone = args.get('phone')
        email_verify_code = args.get('email_verify_code')
        phone_verify_code = args.get('phone_verify_code')
        user = g.user

        if not email and not phone:
            abort(403, error='email和phone没有改动')

        if email:
            if not email_verify_code:
                abort(403, email_verify_code='验证码不能为空')
            cache_code = cache.get(email)
            print(email_verify_code, cache_code)
            if not (email_verify_code == cache_code):
                abort(403, error='验证码错误')
        if phone:
            abort(403, error='暂不支持手机号修改')
        user.email = email
        if not user.save():
            abort(400, error='服务器繁忙，资料修改失败，请重试')
        data = {
            'msg': '资料修改成功',
            'email': email
        }
        return data, 201


class UserChangePassword(Resource):
    @login_required(USER)
    def post(self):
        """
        修改密码
        :return:
        """
        args = parse_change_pwd.parse_args()
        user = g.user
        old = args.get('old')
        new = args.get('new')

        if not user.check_password(old):
            abort(401, error='旧密码不正确')

        user.password = new
        if not user.save():
            abort(400, error='系统繁忙，密码修改失败')

        clear_other_login_caches(USER, user.id)

        data = {
            'msg': 'password has changed successful',
        }

        return data


class UserResetVerify(Resource):
    def post(self):
        args = parse_reset_verify.parse_args()
        email = args.get('email')
        verify_code = args.get('verify_code')

        user = UsersModel.query.filter_by(email=email).first()
        if not user:
            abort(404, error=f'{email} 未注册')

        code = cache.get(email)
        if not (code == verify_code):
            abort(403, error='验证码错误')

        verify_token = generate_verify_token()
        cache.set(verify_token, email, timeout=60 * 5)

        # clear_other_login_caches(USER, user.id)

        data = {
            'msg': 'create reset verify token successful',
            'token': verify_token
        }

        return data


class UserPasswordReset(Resource):
    def post(self):
        args = parse_reset_pwd.parse_args()
        token = args.get('token')
        new = args.get('new')

        email = cache.get(token)
        cache.delete(token)
        user = UsersModel.query.filter_by(email=email).first()
        if not user:
            abort(404, error='未找到此用户')

        user.password = new

        if not user.save():
            abort(400, error='系统繁忙，密码修改失败，请稍后再试')

        # 密码重置后清除所有旧cache/session
        clear_other_login_caches(USER, user.id)

        data = {
            'msg': 'change password successful',
        }

        return data


verify_fields = {
    'username': fields.String,
    'email': fields.String,
    'is_verified': fields.String
}

verify_data_fields = {
    'data': fields.Nested(verify_fields),
    'status': fields.Integer,
    'msg': fields.String
}


class VerifyCode(Resource):
    """
    修改邮箱和密码时发送验证码用，但是要用来验证旧邮箱还是验证新邮箱？
    """
    def post(self, arg):
        args = parser_verify_code.parse_args()
        action = args.get('action')
        verify_code = random.randint(1000, 10000)

        if action == 'email':
            if '@' not in arg:
                abort(400, error='邮箱格式有误')
            email = arg

            user = UsersModel.query.filter_by(email=email).first()
            if user:  # 验证新邮箱
                abort(404, error=f'{email} 已注册')

            cache.set(email, verify_code, timeout=60 * 5)
            send_verify_code_by_mail.delay(email, verify_code)

            data = {
                'msg': f'验证码已发送到 {email}'
            }

            return data
        elif action == 'phone':
            abort(404, error='暂未实现')
        else:
            abort(404, error='非法参数')


class GetUsernameResource(Resource):
    def get(self, id):
        user = UsersModel.query.get(id)
        if not user:
            abort(404, error='无此用户')
        data = {
            'id': id,
            'username': user.username
        }
        return data
