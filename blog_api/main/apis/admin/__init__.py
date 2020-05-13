from flask_restful import reqparse

parser_base = reqparse.RequestParser()
parser_base.add_argument('action', type=str, required=True, help='请输入请求参数')
parser_base.add_argument('username', type=str, required=True, help='请输入用户名')
parser_base.add_argument('password', type=str, required=True, help='请输入密码')
