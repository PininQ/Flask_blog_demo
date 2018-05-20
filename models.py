# -*- coding: utf-8 -*-
__author__ = 'QB'

from werkzeug.security import check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:qiu66666@127.0.0.1/flask_blog"
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 绑定app至SQLAlchemy
db = SQLAlchemy(app)


# 用户数据模型
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号id
    account = db.Column(db.String(20), nullable=False)  # 账号非空
    pwd = db.Column(db.String(100), nullable=False)  # 密码非空
    add_time = db.Column(db.DateTime, nullable=False)  # 注册时间

    # 查询时的返回
    def __repr__(self):
        return "<User %r>" % self.account

    # 检查密码是否正确
    def check_pwd(self, pwd):
        return check_password_hash(self.pwd, pwd)


# 文章数据模型
class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)  # 编号id
    title = db.Column(db.String(100), nullable=False)  # 标题非空
    category = db.Column(db.Integer, nullable=False)  # 编号id
    user_id = db.Column(db.Integer, nullable=False)  # 作者
    logo = db.Column(db.String(100), nullable=False)  # 封面
    content = db.Column(db.Text, nullable=False)  # 内容
    add_time = db.Column(db.DateTime, nullable=False)  # 发布时间

    # 查询时的返回
    def __repr__(self):
        return "<Article %r>" % self.title


# 执行创建表语句
if __name__ == "__main__":
    # 创建表
    db.create_all()
