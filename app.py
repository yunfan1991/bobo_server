from flask import Flask, render_template, \
    current_app, request, make_response, redirect, url_for, flash, jsonify
import urllib.parse
from datetime import timedelta, datetime, time
import json
from flask_restful import reqparse, abort, Api, Resource
import os, requests

from flask_paginate import Pagination, get_page_args
from utils import pagenation_replace, get_ip, redirect_back, url_replace_1, url_replace_2
from flask import session
from flask import Flask, request
import datetime, urllib

import json, uuid
from flask_cors import CORS
from flask_babel import Babel, gettext as _

from utils import get_parse, get_douban, pure_movie_name, get_api, get_host_ip, get_ip

import redis

# from flask_login import LoginManager, login_required

import time, hashlib

from urllib.parse import quote, unquote, urlencode
import webvtt

r = redis.Redis(host='127.0.0.1', port=6379, password='', db=0, decode_responses=True)
media_server = '/media'
#media_server = '/Users/lin/Movies'
import logging

logging.basicConfig(filename=media_server + '/bobo_server.log', level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = '_5#y2L"F4Q8z\n\xecasfe#@!%]/'
app.config['_COOKIE_KEY'] = 'eafe(*)YDVV^Y#WFdafdawe-0='
app.config['COOKIE_NAME'] = 'BOBO_cookie'
app.config['EXPIRES'] = 315360000
app.config['LANGUAGES'] = {
    'en': 'English',
    'zh': '中文',
    'ru': 'русский'
}
babel = Babel(app)


@babel.localeselector
def get_locale():
    try:
        language = r.get('language')
    except:
        language = None
    if language is not None:
        return language
    else:
        return 'en'
    # return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


@app.context_processor
def inject_conf_var():
    return dict(AVAILABLE_LANGUAGES=app.config['LANGUAGES'],
                CURRENT_LANGUAGE=r.get('language'))


@app.template_filter('url_encode')
def urlencode_filter(s):
    movie_address = s
    movie_address = movie_address.replace('//\\', '/')
    movie_address = movie_address.replace('//', '/')
    movie_address = movie_address.replace(r'\/', '/')
    movie_address = movie_address.replace('/\\', '/')
    movie_address = movie_address.replace('/\\', '/')
    encode_data = quote(movie_address)
    return encode_data


@app.template_filter('subtitle')
def urlencode_filter(s):
    movie_address = s
    temp_s = s.split('8567')
    server = temp_s[0] + '8567'
    # logging.info('next address1:',temp_s)
    movie_address = temp_s[-1]
    movie_address = movie_address.replace('//', '/')
    movie_address = movie_address.split('/')

    file_name = movie_address[-1]
    base = os.path.basename(file_name)
    current_language = False
    for key, language in app.config['LANGUAGES'].items():
        subtitle_name = media_server + "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[
            0] + '.' + key + '.srt'
        vtt = "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[0] + '.' + key + '.vtt'
        # logging.info('subtitle name', subtitle_name)
        if key == r.get('language'):
            if os.path.exists(media_server + vtt):
                current_language = True
                return server + vtt
            elif os.path.exists(subtitle_name):
                webvtt.from_srt(subtitle_name).save()
                current_language = True
                return server + vtt
    if not current_language:
        for key, language in app.config['LANGUAGES'].items():
            subtitle_name = media_server + "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[
                0] + '.' + key + '.srt'
            vtt = "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[0] + '.' + key + '.vtt'
            # logging.info('subtitle name', subtitle_name)
            if os.path.exists(media_server + vtt):
                return server + vtt
            elif os.path.exists(subtitle_name):
                webvtt.from_srt(subtitle_name).save()
                return server + vtt

    for key in range(6):
        key = str(key)
        subtitle_name = media_server + "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[
            0] + '.' + key + '.srt'
        vtt = "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[0] + '.' + key + '.vtt'
        # logging.info('subtitle name', subtitle_name)
        if os.path.exists(media_server + vtt):
            return server + vtt
        elif os.path.exists(subtitle_name):
            webvtt.from_srt(subtitle_name).save()
            return server + vtt
    subtitle_name = media_server + "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[
        0] + '.srt'
    vtt = "/".join(movie_address[0:-1]) + '/' + os.path.splitext(base)[0] + '.vtt'
    # logging.info('subtitle name', subtitle_name)
    if os.path.exists(media_server + vtt):
        return server + vtt
    elif os.path.exists(subtitle_name):
        webvtt.from_srt(subtitle_name).save()
        return server + vtt

    return ''


@app.template_filter('next_episode')
def next_episode(s):
    data = ''
    try:
        temp_s = s.split('8567')
        # logging.info('next address1:',temp_s)
        movie_address = temp_s[-1]

        movie_address = movie_address.replace('//', '/')

        movie_address = movie_address.split('/')
        file_name = movie_address[-1]
        # logging.info('next address movie_address:', movie_address)
        dir_name = ":".join(movie_address[0:-1])
        # logging.info('next address dir name',dir_name)
        files_new = r.get('media_server' + dir_name + ':files')
        files = json.loads(files_new)
        files = sorted(files, key=lambda x: (x[1]))
        i = 0
        for item in files:
            i = i + 1
            if file_name == item[1]:
                data = files[i][1]
                data = session['web_server'] + 'play?movie_address=' + dir_name.replace(':', '/') + '/' + data + '$_$' + \
                       files[i][2] + '$_$' + session['host_ip']
                # data = quote(data)
                # logging.info('next address', data)
                break
    except:
        pass
    return data


@app.template_filter('pure_name')
def pure_name(s):
    return pure_movie_name(s)


def list_min(list1, list2):
    list3 = [i for i in list1 if i not in list2]
    return list3


def create_cookie(get_user):
    expires = str(int(time.time() + app.config['EXPIRES']))
    s = '^^^%s^^^%s^^^%s' % (
        r.get('server_address'), expires, app.config['_COOKIE_KEY'])
    L = [r.get('server_address'), expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '^^^'.join(L)


def check_cookie():
    L = None
    try:
        cookie_str = request.cookies.get(app.config['COOKIE_NAME'])
        L = cookie_str.split('^^^')
    except:
        pass
    return L


def list_min(list1, list2):
    list3 = [i for i in list1 if i not in list2]
    return list3


def ip_port(host_ip):
    ip = host_ip.split(':')
    if len(ip) == 1:
        port = '80'
    else:
        port = ip[1]
    ip = ip[0]
    return [ip, port]


from functools import wraps
from flask import g, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not session['user']:
                return redirect(url_for('login', next=request.url))
        except:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@login_required
def index():
    try:
        is_cookie = check_cookie()
        if is_cookie:
            # logging.info('index from cookie')
            session['host_ip'] = is_cookie[0]
        # _thread.start_new_thread(get_available_ip, (1 , 2))
        return redirect('/f')

        # return render_template('index.html', movies=movies, server=server)

    except Exception as e:
        logging.info(e)
        # return redirect(url_for('login'))
        return redirect('/login')


@app.route('/feedback')
def feedback():
    uid = '1cfdabde150c7a9bbe501d9704b79dbf7c947fa8'
    return render_template('feedback.html', uid=uid)


@app.route('/login', methods=['get', 'post'])
def login():
    data = {}
    study = False
    # logging.info('netx', request.args.get('next'))
    session['user'] = False
    if request.method == 'POST':
        data = request.form
        # #logging.info(data['pin_code'])
        # #logging.info(settings_obj.normal_pin)
        try:
            language = data['set_language']
            if language:
                r.set('language', language)
                return redirect('/login/init')
        except:
            pass
        try:
            pd = data['pin_code'] == r.get('normal_pin') or data['pin_code'] == r.get('study_pin')
            study = data['pin_code'] == r.get('study_pin')
            normal = data['pin_code'] == r.get('normal_pin')
        except:
            flash(_('Authentication failed'))
            return redirect('/login')
        if study:
            session['user'] = 'study'
        if normal:
            session['user'] = 'normal'
        if pd:
            # logging.info('getting user')
            session['host_ip'] = r.get('media_server')
            session['web_server'] = r.get('server_address')

            check_box = data['check_box']
            if str(check_box) == 'on':
                # logging.info('to set cookies...')
                cookie_value = create_cookie(data['pin_code'])
                response = make_response(redirect(url_for('index')))
                response.set_cookie(app.config['COOKIE_NAME'], cookie_value)
                # logging.info(str(cookie_value))
                return response
            else:
                next = urllib.parse.unquote(request.args.get('next')).replace(r.get('server_address'), '')
                if next:
                    response = make_response(redirect(next))

                else:
                    response = make_response(redirect(url_for('index')))
                return response

        else:
            flash(_('Authentication failed'))
            return redirect('/login')
    else:
        # select Lang
        if not r.get('language'):
            return render_template('login.html', set_language=True)

    return render_template('login.html')


@app.route('/login/init', methods=['get', 'post'])
def login_init():
    data = {}
    url = ''
    is_init = r.get('is_init')
    if request.method == 'POST':
        '''
        is_init = BooleanField(default=False)
        language = StringField(default='Chinese')
        normal_pin = IntField(default=9999)
        study_pin  = IntField(default=1234)
        api_key = StringField()
        server_address = StringField()
        media_server = StringField()
        q_a = StringField()
        
        '''
        if is_init == 'True':
            data = request.form['q_a']
            # add_obj = Seetings.objects.first()
            if str(data) == r.get('q_a'):
                r.set('is_init', '')
                flash(_('Certification successful, please reinitialize'))
            else:
                flash(_('Authentication failed'))
            return redirect('/login/init')

        else:
            data = request.form
            # #logging.info(str(data.to_dict()))
            data = data.to_dict()
            data['api_key'] = get_api()

            # logging.info(data)
            '''
            {'language': 'Chinese', 'server_address': 'http://127.0.0.1:5000', 'media_server': 'http://127.0.0.1:5000', 'normal_pin': '9999', 'study_pin': '1234', 'q_a': 'Alpha', 'api_key': 'e4b93eb4-0915-11ea-98cf-8c859072f2dc'}
            '''
            for key, value in data.items():
                r.set(key, value)
            with open('config/api_server.txt', 'w') as f:
                f.write(data['server_address'])
            r.set('is_init', 'True')
            flash(_('Parameter setup was successful'))
            return redirect('/login')

    else:
        url = request.base_url.replace('/login/init', '')

    templateData = {
        'title': 'Initial',
        'url': url,
        'is_init': is_init,
        # 'api_key': api_key,
        # 'pagenation_replace': utils.pagenation_replace
    }
    return render_template('login_init.html', **templateData)


@app.route('/code')
@login_required
def invite_code():
    api_key = get_api()
    url = 'http://www.wulibobo.com/invite_code?api_key=' + api_key
    c = requests.get(url)
    code = c.text
    templateData = {
        'title': 'Invite code',
        'code': code,
        # 'api_key': api_key,
        # 'pagenation_replace': utils.pagenation_replace
    }
    return render_template('invite_code.html', **templateData)


@app.route('/login_by_scan', methods=['get'])
def login_by_scan():
    if request.method == 'GET':
        data = request.args.to_dict()
        logging.info(data)
        # if check_box on,使用cookies记录
        # return data
        # data = {}
        study = False
        normal = False
        session['user'] = False

        try:
            pd = data['pin_code'] == r.get('normal_pin') or data['pin_code'] == r.get('study_pin')
            study = data['pin_code'] == r.get('study_pin')
            normal = data['pin_code'] == r.get('normal_pin')
        except:
            flash(_('Authentication failed'))
            return redirect('/login')
        if study:
            session['user'] = 'study'
        if normal:
            session['user'] = 'normal'
        if pd:
            # logging.info('getting user')
            session['host_ip'] = r.get('media_server')
            session['web_server'] = r.get('server_address')
            cookie_value = create_cookie(data['pin_code'])
            response = make_response(redirect(url_for('index')))
            response.set_cookie(app.config['COOKIE_NAME'], cookie_value)
            # logging.info(str(cookie_value))
            return response
        else:
            flash(_('Authentication failed'))
            return redirect('/login')


@app.route('/logout')
@login_required
def logout():
    response = make_response(redirect(url_for('login')))  # 退出后跳转页面
    response.set_cookie(app.config['COOKIE_NAME'], '-delete-')
    # remove the username from the session if it's there
    session.pop('user')
    # session.pop('api_key')
    session.pop('host_ip')
    return response




class movie_list(Resource):
    def post(self):
        # args = parser.parse_args()
        # json_data =
        api_ip = request.json
        data = api_ip['data']
        files_acton = data[-1]
        # #logging.info(data)
        api_key = api_ip['api_key']
        host_ip = api_ip['host_ip']

        user_id = api_host(api_key, host_ip)
        # 存入列表里
        # 1 api_key, host_ip 写入用户表
        # 普通电影列表
        s = data[0]
        # logging.info(len(s))
        # logging.info(files_acton)
        op = Add_movies(user_id, s, files_acton)

        '''
        分析所有文件名，查询更新基础电影库并返回相应ID
        需要做的事：
        分析所有文件名，如能分析出电影名，发行时间则可取
        
        
        
        '''

        # op.update_special_scrects()
        # op.write_movie_list()

        return {'status': 'success', 'message': 'updated'}


api.add_resource(movie_list, '/v1/movie_list')


@app.route('/update_bobo')
@login_required
def update_system():
    try:
        logging.info('exec cd /home/bobo_server')
        os.popen('cd /home/bobo_server')
        output2 = os.popen('git pull')
        return output2.read()
    except Exception as e:
        return str(e)


@app.route('/all')
@app.route('/New')
@app.route('/f')
@login_required
def all():
    if session['user']:
        movies = None
        server = None
        page = 1
        offset = 0
        page, per_page, offset = get_page_args()
        per_page = 60
        data_new = r.keys(pattern='media_server:' + '*:files')
        #data_new = r.scan(0, 'media_server:' + '*:files', 100)
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1
        List = []
        for d in data_new[::-1]:
            if 'secret-' not in d:
                for item in json.loads(r.get(d)):
                    ##logging.info(item)
                    List.append(item)
        List = sorted(List, key=lambda x: (x[-1]), reverse=True)
        # logging.info(List)
        # List.sort(lambda x, y: cmp(x[3], y[3]), reverse=True)
        i = (page - 1) * per_page
        List1 = List[i:i + 60]
        pagination = Pagination(page=page, per_page=per_page, total=len(List), record_name='List')
        session['host_ip'] = r.get('media_server')
        template_data = {
            'title': 'BoBo Media',
            'is_active_logistics': 'color: deeppink',
            'data': List1,
            'pagination': pagination,
            'pagenation_replace': pagenation_replace,
            'server': session['host_ip']

        }
        # return str(form.carrier_intro.)
        # return jsonify(List)
        # return render_template('index.html', **template_data)

    else:
        return redirect('/m/?dir=study')

    return render_template('index.html', **template_data)


@app.route('/m/')
@login_required
def m_dir():
    movies = None
    server = None
    is_dir = False
    page = 1
    offset = 0
    page, per_page, offset = get_page_args()
    per_page = 40
    dir_name = ':'.join(request.args.get('dir').split('$_$'))
    # return jsonify(test)
    # for dir_name in dir_list:
    #logging.info('dir_name', dir_name)
    Files = []
    if dir_name == 'movie' or dir_name == 'cartoon':
        data_new = r.keys(pattern='media_server:' + dir_name + '*:files')

    else:
        data_new = r.keys(pattern='media_server:' + dir_name + ':dirs')
        is_dir = True

        files_new = r.keys(pattern='media_server:' + dir_name + ':files')
        # logging.info('本目录下有文件：', files_new)
        for d in files_new[::-1]:
            if 'secret-' not in d:
                for item in json.loads(r.get(d)):
                    # #logging.info(item)
                    Files.append(item)
        Files = sorted(Files, key=lambda x: (x[1]))
        # logging.info('files',Files)

    # data_new = r.keys(pattern='media_server:' + '*' + dir_name + ':dirs')

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    List = []
    for d in data_new[::-1]:
        if 'secret-' not in d:
            for item in json.loads(r.get(d)):
                # #logging.info(item)
                List.append(item)
    List = sorted(List, key=lambda x: (x[-1]), reverse=True)
    # logging.info(List)
    # List.sort(lambda x, y: cmp(x[3], y[3]), reverse=True)
    i = (page - 1) * per_page
    List1 = List[i:i + 40]
    pagination = Pagination(page=page, per_page=per_page, total=len(List), record_name='List')
    template_data = {
        'title': 'BOBO Media Server',
        'is_active_logistics': 'color: deeppink',
        'movies': List1,
        'pagination': pagination,
        'pagenation_replace': pagenation_replace,
        'cate': dir_name,
        'is_dir': is_dir,
        'files': Files

    }
    # return str(form.carrier_intro.)
    # return jsonify(List)
    # return render_template('index.html', **template_data)
    session['host_ip'] = r.get('media_server')

    return render_template('movies_dir_list.html', **template_data)


@app.route('/search/')
@login_required
def search():
    movies = None
    server = None
    is_dir = False
    page = 1
    offset = 0
    page, per_page, offset = get_page_args()
    per_page = 40
    dir_name = request.args.get('q')
    # return jsonify(test)
    # for dir_name in dir_list:
    # logging.info('dir_name', dir_name)
    Files = []

    if session['user'] == 'study':
        data_new = r.keys(pattern='media_server:study:*' + dir_name + '*:dirs')
        is_dir = True
        files_new = r.keys(pattern='media_server:study:*' + dir_name + '*:files')
    else:
        data_new = r.keys(pattern='media_server:*' + dir_name + '*:dirs')
        is_dir = True
        files_new = r.keys(pattern='media_server:*' + dir_name + '*:files')
        # logging.info('本目录下有文件：', files_new)
    for d in files_new[::-1]:
        if 'secret-' not in d:
            for item in json.loads(r.get(d)):
                # #logging.info(item)
                Files.append(item)
    Files = sorted(Files, key=lambda x: (x[1]))
    # logging.info('files',Files)

    # data_new = r.keys(pattern='media_server:' + '*' + dir_name + ':dirs')

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    List = []
    for d in data_new[::-1]:
        if 'secret-' not in d:
            for item in json.loads(r.get(d)):
                # #logging.info(item)
                List.append(item)
    List = sorted(List, key=lambda x: (x[-1]), reverse=True)
    # logging.info(List)
    # List.sort(lambda x, y: cmp(x[3], y[3]), reverse=True)
    i = (page - 1) * per_page
    List1 = List[i:i + 40]
    pagination = Pagination(page=page, per_page=per_page, total=len(List), record_name='List')
    template_data = {
        'title': 'BOBO Media Server',
        'is_active_logistics': 'color: deeppink',
        'movies': List1,
        'pagination': pagination,
        'pagenation_replace': pagenation_replace,
        'cate': dir_name,
        'is_dir': is_dir,
        'files': Files

    }
    # return str(form.carrier_intro.)
    # return jsonify(List)
    # return render_template('index.html', **template_data)
    session['host_ip'] = r.get('media_server')

    return render_template('movies_dir_list.html', **template_data)


@app.route('/favorite/add/', methods=['get'])
# @login_required
def favorite_add():
    item = request.args.get('item')
    # logging.info('收藏的args', request.args.to_dict())
    # logging.info('收藏的item', item.split(','))
    if json.dumps(item) not in r.lrange(session['user'] + ':favorite', 0, -1):
        r.rpush(session['user'] + ':favorite', json.dumps(item))
        flash(_('Add Success'))
    else:
        flash(_("It's been collected before!"))
    return redirect('/favorite')


@app.route('/favorite/del/', methods=['get'])
# @login_required
def favorite_del():
    item = request.args.get('item')
    r.lrem(session['user'] + ':favorite', 0, json.dumps(item))
    if json.dumps(item) not in r.lrange(session['user'] + ':favorite', 0, -1):
        flash(_('Deleted!'))
    return redirect('/favorite')


@app.route('/favorite')
@login_required
def favorite():
    movies = None
    server = None
    is_dir = False
    page = 1
    offset = 0
    page, per_page, offset = get_page_args()
    per_page = 40

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    dir_name = ''
    Files = ''
    temp_list = r.lrange(session['user'] + ':favorite', 0, -1)
    List = []
    for item in temp_list:
        List.append(json.loads(item).split(','))
    # List = sorted(List, key=lambda x: (x[-1]), reverse=True)
    logging.info('List', List)
    List.reverse()
    # List.sort(lambda x, y: cmp(x[3], y[3]), reverse=True)
    i = (page - 1) * per_page
    List1 = List[i:i + 40]
    pagination = Pagination(page=page, per_page=per_page, total=len(List), record_name='List')
    template_data = {
        'title': 'BOBO Media Server',
        'is_active_logistics': 'color: deeppink',
        'movies': List1,
        'pagination': pagination,
        'pagenation_replace': pagenation_replace,
        'cate': dir_name,
        'is_dir': is_dir,
        'files': Files,
        'is_favorite': True

    }
    # return str(form.carrier_intro.)
    # return jsonify(List)
    # return render_template('index.html', **template_data)
    session['host_ip'] = r.get('media_server')

    return render_template('movies_dir_list.html', **template_data)


@app.route('/play', methods=['get', 'post'])
# @login_required
def play():
    # logging.info(request.args)
    movie_address = request.args['movie_address']
    if '$_$' in movie_address:
        temp_list = movie_address.split('$_$')
        movie_address = temp_list[0]
        server = temp_list[-1]
        uid = temp_list[1]
    else:
        server = request.args['server']
        uid = request.args['uid']
    movie_address = url_replace_1(movie_address)

    if 'http://' not in server:
        server = 'http://' + request.args['server']
    movie_address = server + movie_address

    # movie_address = url_replace_2(movie_address)
    # movie_address = movie_address.replace('//', '/')
    # movie_address = movie_address.replace(r'\/', '/')
    # movie_address = urllib.parse.quote(movie_address)
    # movie_address = os.path.normpath(movie_address)
    # movie_address = movie_address.decode('utf-8').encode('iso-8859-1')
    # .decode('iso-8859-1').encode('latin1')
    end_with = movie_address.split('.')[-1]
    return render_template('player.html', movie=movie_address, uid=uid, server=server, end_with=end_with)


@app.route('/v1/get_movies', methods=['POST'])
def get_movies():
    data = request.form.getlist('data')
    # logging.info(data)
    # json_data = json.loads(data.decode("utf-8"))
    # #logging.info(json_data)

    return "success!"


if __name__ == '__main__':
    logging.warning('bobo_server start')
    app.run()
