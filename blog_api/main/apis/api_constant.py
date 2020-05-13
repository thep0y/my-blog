import os

from main.settings import BASE_DIR


# 用户登录行为
USER_ACTION_REGISTER = 'register'
USER_ACTION_LOGIN = 'login'
USER_ACTION_LOGOUT = 'logout'
USER_ACTION_VERIFY = 'verify'
USER_ACTION_GET_INFO = 'get'
USER_ACTION_WRITTEN_OFF = 'written_off'

# 管理员管理行为
ADMIN_MANAGE_USER = 'user'
ADMIN_MANAGE_BLOG = 'blog'
ADMIN_MANAGE_IP = 'IP'

# 超级管理员列表(如果有超级管理员的话需要增加超级管理员方法)
SUPER_ADMINS = ['root', 'admin']

# 状态码
HTTP_OK = 200
HTTP_CREATE_OK = 201
HTTP_ERROR = 400
HTTP_NOT_AUTHENTICATION = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_NOT_ALLOWED_METHOD = 405

# 登录token前缀
ADMIN = 'admin-'
USER = 'user-'

# 验证token前缀
VERIFY = 'verify-'
