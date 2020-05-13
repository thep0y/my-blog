from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

parse_file = reqparse.RequestParser()
parse_file.add_argument('file', type=FileStorage, required=True, help='请上传文件', location='files')


class UploadResource(Resource):
    """
    静态文件由前端处理，后端不应该负责保存文件，应该是前端上传文件后将文件名和路径传给后端，后端保存到对应的user或blog的数据库中
    """
    def post(self):
        args = parse_file.parse_args()
        file_ = args.get('file')

        return file_.filename, 201