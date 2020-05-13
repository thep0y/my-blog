import datetime
import re
import time
import uuid

import jwt
import redis
from flask import request, g, current_app
from flask_mail import Message
from flask_restful import abort

from main.apis.api_constant import ADMIN, USER, VERIFY, PAY, HTTP_ERROR, HTTP_FORBIDDEN, HTTP_NOT_AUTHENTICATION
from main.ext import cache, mail
from main.models.admin.admin_model import AdminModel
from main.models.user.user_model import UsersModel
from main.settings import REDIS_HOST, celery


def generate_token(prefix):
    token = prefix + uuid.uuid4().hex
    return token


def generate_admin_token():
    return generate_token(ADMIN)


def generate_user_token():
    return generate_token(USER)


def generate_verify_token():
    return generate_token(VERIFY)


def get_user(model, arg):
    if not arg:
        return None
    # 如果传入的参数是id（int）
    if type(arg) == int:
        user = model.query.get(arg)
        if user:
            return user
    # 如果传入的参数是用户名（str）
    if type(arg) == str:
        user = model.query.filter(model.username == arg).first()
        if user:
            return user
    return None


def get_admin_user(arg):
    return get_user(AdminModel, arg)


def get_ordinary_user(arg):
    return get_user(UsersModel, arg)


def check_user_exits(username: str = None, email: str = None, phone: int = None):
    # 注册时检查用户名、邮箱和手机号是否唯一
    if not username or not email:
        abort(403, error='用户名或邮箱不能为空！')
    if username:
        user = UsersModel.query.filter(UsersModel.username == username).first()
        if user:
            abort(400, error='用户名已存在')
    if email:
        user = UsersModel.query.filter(UsersModel.email == email).first()
        if user:
            abort(400, error='邮箱已注册')
    if phone:
        user = UsersModel.query.filter(UsersModel.phone == phone).first()
        if user:
            abort(400, error='手机号已注册')


def _verify(user_type):
    token = request.args.get('token') or request.form.get('token')
    if not token:
        abort(401, error='未登录')
    if not token.startswith(ADMIN) and not token.startswith(USER):
        abort(403, error='未知用户，访问无效')
    if not token.startswith(user_type):
        if user_type == ADMIN:
            abort(401, error='已登录的用户可能不是管理员用户，或者您尚未登录。请登录管理员账户')
        else:
            abort(401, error='已登录的用户可能不是普通用户。')
    user_id = cache.get(token)
    if not user_id:
        abort(401, error='此操作需要登录。如果您之前已登录，可能是登录过期，请重新登录。')
    if user_type == ADMIN:
        user = get_admin_user(user_id)
    else:
        user = get_ordinary_user(user_id)
    if not user:
        abort(401, error='您的账户状态异常，请联系管理员')
    # 如果登录，则将用户和token传到跨域全局变量g中，用于后面的权限认证
    g.user = user
    g.token = token


def login_required(user_type: str):
    def login_required_wrapper(func):
        def wrapper(*args, **kwargs):
            _verify(user_type)
            return func(*args, **kwargs)

        return wrapper

    return login_required_wrapper


# 检查邮箱格式
def check_email(email: str):
    # 可使用字母、数字、下划线，少部分邮箱中间可能有点，需要以字母或数字开头，二级域名只能为字母或数字，顶级域名只能为字母
    pattern = re.compile(r'^[a-zA-Z0-9]+\.?\w+@[a-zA-Z0-9]+\.[a-zA-Z]+$')
    result = pattern.match(email)
    return result


def clear_other_login_caches(prefix: str, user_id: int, db: int = 0):
    """
    由于flask-caching模块未提供遍历所有缓存的方法，所以只能通过redis模块来看所有缓存
    取到所有缓存后，可以用redis也可以用flask-caching来取值，由于flask-caching提供了便捷的取值方法，所以采用flask-caching取值
    对取到的值进行判断，等于当前用户的id就删除，空的也删除
    :param prefix: 要清除缓存的用户的类别，值为 ADMIN 或 USER
    :param user_id: 要清除的用户的id
    :param db: 缓存所在的redis数据库id
    """
    r = redis.Redis(REDIS_HOST[:-5], db=db)
    all_keys = r.keys()
    cache_prefix_len = len('cache:')
    keys = [key.decode('utf-8')[cache_prefix_len:] for key in all_keys if prefix in key.decode('utf-8')]
    for key in keys:
        value = cache.get(key)
        if value == user_id or not value:
            cache.delete(key)


def get_now_time():
    now_raw = datetime.datetime.now()
    now = datetime.datetime.strftime(now_raw, '%Y-%m-%d %H:%M:%S')
    return now_raw, now


def generate_jwt_token(user_id=None):
    if not user_id:
        abort(400, error='用户id不能为空')
    token_dict = {  # payload
        'iat': int(time.time()),  # 时间戳，只能是整型
        'user_id': str(user_id)  # 需验证的识别参数
    }
    headers = {  # headers
        'alg': 'HS256'  # 加密算法
    }
    jwt_token = jwt.encode(
        token_dict,
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
        headers=headers,
    )

    return jwt_token.decode('ascii')


def parse_jwt_token(token):
    try:
        data = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms='HS256'
        )
    except Exception as e:
        print(e)
        data = None
    return data


def get_logined_user(prefix: str, token: str):
    """
    判断token是否有效，返回user
    :param prefix:
    :param token:
    :return: 返回通过token查到的UsersModel或AdminModel对象
    """
    user_id = cache.get(token)
    if not user_id:
        abort(HTTP_NOT_AUTHENTICATION, error='用户未登录或登录过期，请重新登录')

    if prefix == USER:
        user = UsersModel.query.get(user_id)
    elif prefix == ADMIN:
        user = AdminModel.query.get(user_id)
    else:
        user = None

    if not user:
        abort(HTTP_NOT_AUTHENTICATION, error='用户不存在')

    return user, user_id


@celery.task
def send_verify_code_by_mail(email: str = None, verify_code: int = None):
    if email and verify_code:
        app = current_app._get_current_object()
        msg = Message(subject='请验证您的邮箱', recipients=[email])
        msg.html = f'''
        <p>您正在修改Blog邮箱，</p>
        <span>此次操作的验证码为：</span>
        <br>
        <p style="color: red; font-size: 30px;">{verify_code}</p>
        <p>如果这不是您本人的操作，可能您的密码已泄露，请及时修改或重置密码。</p>
        <br><span>(验证码有效期为5分钟)</span>
        '''
        with app.app_context():
            mail.send(msg)
        return True
    else:
        return False


def verify_user_password(prefix: str, arg: str, password: str):
    # admin和user登录时的密码验证
    if not arg:
        abort(HTTP_ERROR, error='用户名或邮箱不能为空！')
    if prefix == ADMIN:  # 如果是admin
        user = AdminModel.query.filter(AdminModel.username == arg).first()
    elif prefix == USER:  # 如果是user
        if '@' in arg:  # 如果是邮箱
            user = UsersModel.query.filter(UsersModel.email == arg).first()
        else:
            user = UsersModel.query.filter(UsersModel.username == arg).first()
    else:
        user = None
        abort(HTTP_FORBIDDEN, error='非法的用户前缀')

    if not user:
        abort(HTTP_NOT_AUTHENTICATION, error='用户不存在')
    if not user.check_password(password):
        abort(HTTP_NOT_AUTHENTICATION, error='用户名和密码不匹配')

    return user


def handle_searched_content(content: str, key_word: str) -> str:
    """
    处理过长的搜索结果，截取匹配到的第一个关键词前后40个字符
    """

    content = '，'.join(re.findall(u'([0-9A-Za-z\u4e00-\u9fa5]+)',content))  # 删掉评论中的markdown格式只保留汉字、字母、数字

    first_index = content.find(key_word)
    if -1 < first_index <= 40:
        result = content[0: first_index + 40]
    else:
        result = content[first_index - 40:first_index + 40]
    return result.replace(key_word, f'<span class="keyWord">{key_word}</span>')
