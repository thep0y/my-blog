import datetime
import os
import uuid

from flask import Blueprint, request, render_template, jsonify, flash, redirect, url_for, session, g

from main.settings import BASE_DIR

blue = Blueprint('blue', __name__)


@blue.route('/')
def index():
    return render_template('index.html')


@blue.route('/register/')
def register():
    return render_template('register.html')


@blue.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@blue.route('/logout/')
def logout():
    return redirect(url_for('blue.login'))


@blue.route('/verified/')
def verified():
    return render_template('verified.html')


@blue.route('/admin/')
def admin():
    # 应该显示主页，主页显示有待审核的文章数量，点击数量进入待审核页面
    return render_template('admin/getTypes.html')


@blue.route('/admin/login/')
def admin_login():
    return render_template('login.html')


@blue.route('/admin/addtypes/')
def admin_add_types():
    return render_template('admin/addTypes.html')


@blue.route('/admin/gettypes/')
def admin_get_types():
    return render_template('admin/getTypes.html')


@blue.route('/admin/ganvas/')
def ganvas():
    return render_template('admin/ganvas.html')


@blue.route('/publish/')
def publish_new_blog():
    return render_template('blog/newBlog.html')


@blue.route('/upload/', methods=['POST'])
def upload_img():
    os.chdir(os.path.join(BASE_DIR, 'main/static/img'))
    img = request.files.get('img')
    old_name = img.filename.split('.')
    suffix = old_name[-1]
    now = datetime.datetime.now()
    today = datetime.datetime.strftime(now, '%Y%m%d')
    filename = uuid.uuid4().hex
    if not os.path.exists(today):
        os.makedirs(today, 755)
    img.save(f'{today}/{filename}.{suffix}')
    return jsonify(
        {'msg': 'the image has uploaded successful.', 'filename': f'{today}/{filename}.{suffix}',
         'oldName': old_name[0]})


@blue.route('/blog/<int:id>/')
def blog(id):
    text = request.form
    print(text)
    return render_template('blog/blog.html')


@blue.route('/user/<int:id>/')
def user(id):
    return render_template('user/userBlog.html')


@blue.route('/myblog/')
def my_blog():
    return render_template('user/myBlog.html')


@blue.route('/comments/<int:id>')
def my_comments(id):
    return render_template('user/myComments.html')


@blue.route('/type/<int:id>/')
def type_blog(id):
    return render_template('blog/typeBlog.html')


@blue.route('/myfavorite/')
def my_favorite():
    return render_template('user/myFavorite.html')


@blue.route('/account/')
def account():
    return render_template('user/account.html')


@blue.route('/audit/<int:id>/')
def audit(id):
    return render_template('admin/audit.html')


@blue.route('/search/')
def search():
    return render_template('search.html')
