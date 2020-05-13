from smtplib import SMTPDataError

from flask import current_app
from flask_mail import Message

from main.ext import mail
from main.settings import SERVER_HOST, celery


@celery.task
def send_mail(email: str = None, token: str = None):
    if email and token:
        app = current_app._get_current_object()
        url = f'{SERVER_HOST}user?action=verify&token={token}'
        msg = Message(subject='请验证您的邮箱', recipients=[email])
        msg.html = f'''
        <p>欢迎注册Blog，</p>
        <span>点击下面的链接验证您的邮箱：</span>
        <br>
        <a href={url}>点我验证</a>
        <p>如果上面的链接无法点击，请复制下面的链接到浏览器中打开：</p>
        <p>{url}</p>
        <br><span>(链接有效期为5分钟)</span>
        '''
        try:
            with app.app_context():
                mail.send(msg)
            return True
        except SMTPDataError:
            return False
    else:
        return False
