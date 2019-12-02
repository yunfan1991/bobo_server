import json
import os
import re
from flask import request, redirect, url_for
import socket
import requests, PTN
import time, uuid


# from app import db
# from models import *
def get_host_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('119.29.29.29', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_api():
    # 先判断本地有没有api.txt，有就取值
    uuid_address = None
    try:
        with open(os.path.join(os.path.abspath('.'), 'config/api_key.txt'), 'xt') as f:
            uuid_address = str(uuid.uuid1())
            f.write(uuid_address)
            print('Generate new_api', uuid_address)
    except:
        with open(os.path.join(os.path.abspath('.'), 'config/api_key.txt'), 'r') as f:
            uuid_address = f.read()
            # print('open api.txt .....')
            print('current_api', uuid_address)
    return uuid_address


def save_send_api_ip(api_key, host_ip, api_server):
    try:
        with open('config/' + api_key + '.txt', 'r') as f:
            ip = f.read()
            if ip != host_ip:
                with open(api_key + '.txt', 'w') as f:
                    f.write(host_ip)
                r = requests.post(api_server + "/v1/write_user", json={"api_key": api_key, 'host_ip': host_ip})

    except:
        # 没有就生成一个新的并写入文件api.txt
        with open(api_key + '.txt', 'w') as f:
            f.write(host_ip)
    r = requests.post(api_server + "/v1/write_user", json={"api_key": api_key, 'host_ip': host_ip})


def get_parse(movie):
    if '][' in movie:
        movie = movie.replace('][', '.')
        movie = movie.replace('[', '')
        movie = movie.replace(']', '')
    name_list = ['[电影天堂www.dy2018.com]',
                 '阳光电影www.ygdy8.com.',
                 '[6v电影www.dy131.com]',
                 '影音馆',
                 '【电影家园www.idyjy.com下载】',
                 '最新电影www.66e.cc】',
                 '6v电影www.dy131.com】']
    for n in name_list:
        movie = movie.replace(n, '')

    info = PTN.parse(movie)
    info['name_chinese'] = ''
    info['name_english'] = ''
    p = re.compile(u'[\u4e00-\u9fa5]+')
    try:
        if info['year']:
            pass
    except:
        info['year'] = ''
    if '.' in info['title']:
        info['title'] = info['title'].split('.')[0]
    if p.search(info['title']):
        s = info['title']
        # print('has chinese....', s)
        uncn = re.compile(r'[\u0061-\u007a,\u0020]')
        en = "".join(uncn.findall(s.lower()))
        # print('en', en)
        # s = s.replace(' ', '')
        s1 = s.lower().replace(en, '')
        # print('s1...', s1)
        if len(s) > len(s1):
            info['name_chinese'] = s1.strip()
            info['name_english'] = info['title'].replace(s1, '').strip()
        info['title'] = info['title'].strip()
        info['title'] = info['title'].replace('mp4', '')
        if info['title'].endswith('Movi'):
            info['title'].replace('Movi', 'Movie')
    if info['name_chinese'] == '':
        info['name_chinese'] = info['title']

    # pprint.pprint(info)

    return info


def pure_movie_name(movie_name):
    info = get_parse(movie_name)
    # pprint.pprint(info)
    episode = ''
    season = ''
    audio = ''
    year = ''
    try:
        if info['year']:
            year = ' - ' + str(info['year'])
        if info['name_chinese']:
            name = info['name_chinese']
            return name + str(year)
        elif info['title']:
            return info['title'] + str(year)
        else:
            return info['name_english'] + str(year)
    except:
        return movie_name[0:30] + str(year)


def get_douban(movie, year=None):
    movie = movie.split('BD')[0]
    movie = movie.split('HD')[0]
    movie = movie.split('1024')[0]
    if year:
        # 0df993c66c0c636e29ecbb5344252a4a
        # 0b2bdeda43b5688921839c8ecb20399b
        url = 'http://t.yushu.im//v2/movie/search?q=' + str(
            movie) + ',' + str(
            year)
    else:
        url = 'http://t.yushu.im//v2/movie/search?q=' + str(
            movie)
    page = requests.get(url, timeout=15)
    content = page.content
    content = json.loads(content)
    time.sleep(1)
    try:
        return content['subjects'][0]
    except:
        return False


import pprint


def url_replace_1(movie_address):
    movie_address = movie_address.replace('//\\', '/')
    movie_address = movie_address.replace('//', '/')
    movie_address = movie_address.replace(r'\/', '/')
    movie_address = movie_address.replace('/\\', '/')
    movie_address = movie_address.replace('/\\', '/')

    return movie_address


def url_replace_2(movie_address):
    #
    r_d = {'!': '%21', '*': '%2A', '"': '%22', "'": '%27', '(': '%28', ')': '%29', ';': '%3B', '@': '%40',
           '&': '%26', '=': '%3D', '+': '%2B', '$': '%24', ',': '%2C', '?': '%3F', '#': '%23',
           '[': '%5B', ']': '%5D'}
    for k, v in r_d.items():
        movie_address = movie_address.replace(k, v)
    return movie_address


def get_ip():
    if request.remote_addr and request.remote_addr != '127.0.0.1':
        return request.remote_addr
    else:
        return request.headers['X-Forwarded-For']


def check_server_ip(ips):
    ip, port = ips[0], ips[1]
    sep = ip.split('.')
    if len(sep) != 4:
        return False
    for i, x in enumerate(sep):
        try:
            int_x = int(x)
            if int_x < 0 or int_x > 255:
                return False
        except:
            return False
    return True


try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='app.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


# save_img('https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2541093820.jpg','111','111')


def delete_duplicate_words(sentence):
    # remove punctuation
    # the unicode flag makes it work for more letter types (non-ascii)
    no_punc = re.sub(r'[^\w\s]', '', sentence, re.UNICODE)
    re_output = re.sub(r'\b(\w+)( \1\b)+', r'\1', no_punc)
    print('No duplicates:', re_output)
    return re_output


def pagenation_replace(pagenation):
    pagenation = str(pagenation)
    pagenation = pagenation.replace('div class="pagination"',
                                    'nav class="pagination is-centered" role="navigation" aria-label="pagination"')
    pagenation = pagenation.replace('</div>', '</nav>')
    pagenation = pagenation.replace('<ul>', '<ul class="pagination-list">')
    pagenation = pagenation.replace('<li class="previous disabled unavailable"><a>',
                                    '<li><a class="pagination-previous">')
    pagenation = pagenation.replace('<li class="next"><a', '<li><a class="pagination-next" ')
    pagenation = pagenation.replace('<li class="active"><a',
                                    '<li><a class="pagination-link is-current" aria-current="page" ')
    pagenation = pagenation.replace('<a href', '<a class="pagination-link" href ')

    return pagenation
