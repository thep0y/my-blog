from werkzeug.security import generate_password_hash, check_password_hash

from main.ext import db


class Base(db.Model):
    __abstract__ = True  # 抽象化，不生成表
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False


class UserBaseModel(Base):
    __abstract__ = True
    username = db.Column(db.String(15), unique=True, nullable=False)
    _password = db.Column(db.String(256))

    @property
    def password(self):
        raise AttributeError('不可访问')

    @password.setter
    def password(self, pwd):
        self._password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self._password, pwd)


