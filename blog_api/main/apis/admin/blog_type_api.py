import re

from flask_restful import Resource, fields, marshal, reqparse, abort
from sqlalchemy.exc import IntegrityError

from main.apis.api_constant import ADMIN, HTTP_ERROR
from main.apis.utils import login_required
from main.ext import db
from main.models.blog.blog_model import BlogTypeModel

type_fields = {
    'id': fields.Integer,
    'type': fields.String
}

types_data = {
    'msg': fields.String,
    'data': fields.List(fields.Nested(type_fields))
}

parse = reqparse.RequestParser()
parse.add_argument('type', type=str, required=True, help='请输入要增加的文章类型')

parse_del = reqparse.RequestParser()
parse_del.add_argument('id', type=int, required=True, help='请输入要删除的类型id')

parse_change = reqparse.RequestParser()
parse_change.add_argument('oldType', type=str, required=True, help='请输入要修改的原类型名')
parse_change.add_argument('newType', type=str, required=True, help='请输入要修改的新类型名')


class BlogTypeManage(Resource):
    def get(self):
        """
        任何人都可以查询文章类型
        """
        blog_types = BlogTypeModel.query.all()

        data = {
            'msg': 'ok',
            'data': blog_types
        }

        return marshal(data, types_data)

    @login_required(ADMIN)
    def post(self):
        args = parse.parse_args()
        type_ = args.get('type')

        types = type_.split('#')

        for i in types:
            blog_type = BlogTypeModel()
            blog_type.type = i
            db.session.add(blog_type)
        try:
            db.session.commit()
        except IntegrityError as e:
            err = str(e.orig)
            if 'Duplicate' in err:
                duplicate = re.search(r"Duplicate entry '(.*?)' for", err)
                abort(HTTP_ERROR, error=f'类型 `{duplicate.groups()[0]}` 已存在！请勿重复添加！')
        finally:
            db.session.close()

        blog_types = BlogTypeModel.query.all()

        data = {
            'msg': '添加类型成功',
            'data': blog_types
        }

        return marshal(data, types_data), 201

    @login_required(ADMIN)
    def delete(self):
        args = parse_del.parse_args()
        type_id = args.get('id')

        type_ = BlogTypeModel.query.get(type_id)
        if not type_:
            abort(404, error=f'id 为 {type_id} 的类型不存在')
        if not type_.delete():
            abort(400, error='服务器繁忙，暂时无法完成删除操作')

        data = {
            'msg': '删除成功',
            'data': marshal(type_, type_fields)
        }

        return data

    @login_required(ADMIN)
    def put(self):
        args = parse_change.parse_args()
        old_type = args.get('oldType')
        new_type = args.get('newType')
        print(old_type)
        blog_type = BlogTypeModel.query.filter_by(type=old_type).first()
        if not blog_type:
            abort(404, error='要修改的原类型不存在')
        blog_type.type = new_type

        db.session.commit()

        data = {
            'msg': '类型修改成功',
            'oldType': old_type,
            'newType': new_type
        }

        return data
