# -*- coding: utf-8 -*-
__author__ = 'QB'

import uuid

from datetime import datetime
import os
from flask import Flask, render_template, redirect, url_for, flash, session, Response, request
from forms import LoginForm, RegisterForm, ArticleAddForm, ArticleEditForm
from models import User, db, Article
from models import app

from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app.config['SECRET_KEY'] = 'qinbin'
# 设置上传封面图路径
app.config['uploads'] = os.path.join(os.path.dirname(__file__), 'static/uploads')


# 登录装饰器：限制用户在未登录状态不能访问list等需要登录的页面
def user_login_req(f):  # 装饰器传入一个函数，判断包装过后的函数对象。
    @wraps(f)
    def login_req(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return login_req


@app.route('/', methods=['GET'])
def index():
    return redirect('/login/')


# login 用户登录
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        session['user'] = data['account']
        flash('登录成功', 'ok')
        return redirect('/blog/list/1/')
    # 返回渲染模板
    return render_template('login.html', title='登录', form=form)


# logout 用户退出(302跳转到登录页面)
@app.route('/logout/', methods=['GET'])
@user_login_req
def logout():
    # 重定向到指定的视图对应的url，蓝图中才可以使用
    # return redirect(url_for('app.login'))
    # 调用session的pop功能将user变为None
    session.pop('user', None)
    # 直接跳转路径
    return redirect('/login/')


# register 用户注册
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        # 保存数据
        user = User(
            account=data['account'],
            # 对于pwd进行加密
            pwd=generate_password_hash(data['pwd']),
            add_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        db.session.add(user)
        db.session.commit()
        # 定义一个会话的闪现
        flash('注册成功，请登录', 'ok')
        return redirect('/login/')
    return render_template('register.html', title='注册', form=form)


# 修改文件名称
def change_name(name):
    # 获取后缀名
    info = os.path.splitext(name)
    # 文件名：时间格式字符串+唯一字符串+后缀名
    name = datetime.now().strftime('%Y%M%D%H%M%S') + str(uuid.uuid4().hex) + info[-1]
    return name


# blog_add 发布文章
@app.route('/blog/add/', methods=['GET', 'POST'])
@user_login_req
def blog_add():
    form = ArticleAddForm()
    if form.validate_on_submit():
        data = form.data

        # 上传logo
        file = secure_filename(form.logo.data.filename)
        logo = change_name(file)
        if not os.path.exists(app.config['uploads']):
            os.makedirs(app.config['uploads'])
        # 保存文件
        form.logo.data.save(app.config['uploads'] + '/' + logo)
        # 获取用户ID
        user = User.query.filter_by(account=session['user']).first()
        user_id = user.id
        # 保存数据，Article
        article = Article(
            title=data['title'],
            category=data['category'],
            user_id=user_id,
            logo=logo,
            content=data['content'],
            add_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        db.session.add(article)
        db.session.commit()
        flash(u'发布文章成功', 'ok')
    return render_template('blog_add.html', title='发布文章', form=form)


# blog_edit 编辑文章
# 传入整型id参数
@app.route('/blog/edit/<int:id>/', methods=['GET', 'POST'])
@user_login_req
def blog_edit(id):
    form = ArticleEditForm()
    article = Article.query.get_or_404(int(id))
    if request.method == 'GET':
        form.content.data = article.content
        form.category.data = article.category
    # 莫名其妙赋初值：不赋初值表单提交时会提示封面为空
    # 放在这里修复显示请选择封面的错误
    form.logo.data = article.logo
    if form.validate_on_submit():
        data = form.data
        # 上传logo
        file = secure_filename(form.logo.data.filename)
        logo = change_name(file)
        if not os.path.exists(app.config['uploads']):
            os.makedirs(app.config['uploads'])
        # 保存文件
        form.logo.data.save(app.config['uploads'] + '/' + logo)
        article.logo = logo
        article.title = data['title']
        article.content = data['content']
        article.category = data['category']
        db.session.add(article)
        db.session.commit()
        flash(u'编写文章成功', 'ok')
    return render_template('blog_edit.html', form=form, title='编辑文章', article=article)


# blog_list 文章列表
@app.route('/blog/list/<int:page>/', methods=['GET'])
@user_login_req
def blog_list(page):
    if page is None:
        page = 1
    # 只展示当前用户才能看到的内容
    user = User.query.filter_by(account=session['user']).first()
    user_id = user.id
    page_data = Article.query.filter_by(
        user_id=user_id
    ).order_by(
        Article.add_time.desc()
    ).paginate(page=page, per_page=1)
    category = [(1, u'Python'), (2, u'MongoDB'), (3, u'Redis')]
    return render_template('blog_list.html', title='文章列表', page_data=page_data, category=category)


# blog_del 删除文章
@app.route('/blog/del/<int:id>/', methods=['GET'])
@user_login_req
def blog_del(id):
    article = Article.query.get_or_404(int(id))
    db.session.delete(article)
    db.session.commit()
    flash('删除《%s》成功！' % article.title, 'ok')
    return redirect('/blog/list/1')


# 设置密钥,保持这个秘密：
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# 验证码
@app.route("/captcha/", methods=["GET"])
def captcha():
    from captcha import Captcha
    c = Captcha()
    info = c.create_captcha()
    image = os.path.join(
        os.path.dirname(__file__),
        'static/captcha') + '/' + info['image_name']
    with open(image, 'rb') as f:
        image = f.read()
    # 进行会话session中值的保存
    session['captcha'] = info['captcha']
    # print(session['captcha'])
    return Response(image, mimetype='jpeg')


if __name__ == '__main__':
    app.run(debug=True)
