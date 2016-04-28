# coding: utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import login_manager, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')  # 在关系的另一个模型中添加反向引用
    default = db.Column(db.Boolean, default=False, index=True)  # 设置用户注册的默认角色
    perssions = db.Column(db.Integer)  # 添加权限

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod  # 装饰器 不需要实例化 直接类名 函数名调用
    def insert_roles():
        roles = {
            'User': (Perssion.FOLLOW |
                     Perssion.COMMENT |
                     Perssion.WRITE_ARTICLES, True),
            'Moderator': (Perssion.FOLLOW |
                          Perssion.COMMENT |
                          Perssion.WRITE_ARTICLES |
                          Perssion.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()  # 进行数据库查找角色
            if role is None:
                role = Role(name=r)
            role.perssions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Perssion:
    FOLLOW = 0x01  # 定义关注用户
    COMMENT = 0x02  # 发表评论
    WRITE_ARTICLES = 0x04  # 写文章
    MODERATE_COMMENTS = 0x08  # 管理他人发表的评论
    ADMINISTER = 0x80  # 管理员权限


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(perssion=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
