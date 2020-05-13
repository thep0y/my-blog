# -*- coding: utf-8 -*-
import time

from flask import request, g, Response, abort

from main.ext import cache


def load_middleware(app):
    @app.before_request
    def before():
        # 如何限制ip访问频率？cache还是用model？
        black_list = cache.get(request.remote_addr)
        if not black_list:
            black_list = []
        black_list.append(time.time())
        cache.set(request.remote_addr, black_list)
        b = cache.get(request.remote_addr)
        if len(b) > 10:
            print(b)
            abort(Response(status=403, response='访问频繁，请10秒后再试！'))
        g.msg = '测试中间件(面向切面编程)和g'

    @app.after_request
    def after(res):
        # print('*' * 30 + '\n这是after')
        # print(res)
        # print(type(res))
        return res
