from flask_wtf.csrf import generate_csrf


def load_middleware(app):  # 暂时用不上
    @app.after_request
    def after_request(response):
        # 调用函数生成csrf token
        csrf_token = generate_csrf()
        # 设置cookie传给前端
        response.set_cookie('csrf_token', csrf_token)
        return response
