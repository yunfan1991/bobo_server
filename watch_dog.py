from utils import *
import hashlib
import os, datetime, json
from watchdog.observers import Observer
from watchdog.events import *
import time
import redis

r = redis.Redis(host='127.0.0.1', port=6379, password='', db=0, decode_responses=True)

# web_server_dir = '/Volumes/video'
web_server_dir = '/media'
dirs = ['movie', 'tv', 'cartoon', 'mtv', 'show', 'special', 'study', 'doc', 'audio']

import logging

logging.basicConfig(filename=web_server_dir + '/watchdog.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    with open('api_server.txt', 'r') as f:
        api_server = f.read()
    api_key = get_api()
except:
    pass

# api_server = 'http://192.168.203.25:5000'
# api_key = get_api()


# api_server = 'https://v.wulibobo.com'
current_dir = os.path.abspath('.')


class bobo_server_main():
    def __init__(self):
        # self.media_server = '/media_server'
        self.media_server = web_server_dir

    def scan(self, directory):
        files_list = []
        specials = {}
        secrets = {}
        tvs = {}
        # 需求：根目录下所有目录皆为redis主key,一级目录下各级目录为副key
        # /cartoon/玩具总动员4.Toy.Story.4.2019.BD1080P.英语中英双字.BTDX8/玩具总动员4.Toy.Story.4.2019.BD1080P.英语中英双字.BTDX8.mp4
        i = 0
        dir_1 = []
        for root, sub_dirs, files in os.walk(directory):
            # root = root.replace(directory, '/')
            # files = [f for f in files if not f[0] == '.']
            sub_dirs[:] = [d for d in sub_dirs if not d[0] == '.']
            if '$RECYCLE.BIN' in sub_dirs:
                sub_dirs.remove('$RECYCLE.BIN')
            if '@eaDir' in sub_dirs:
                sub_dirs.remove('@eaDir')
            if i == 0:
                dir_1 = sub_dirs
                break
            i = i + 1
        # logging.info('根目录', dir_1)
        r.set('media_server:root_dir', json.dumps(dir_1))
        # 遍历一级目录下的目录与文件
        for item in dir_1:
            if 'secret' in item:
                # item = item.split('-')[0]
                r.set('media_server:secret_passowrd', item.split('-')[1])
            dir_2 = []
            i = 0
            walk_path = directory + '/' + item

            fm = ['swf', 'flv', 'avi', 'wmv', 'asf', 'wmvhd', 'mpeg', 'dat', 'vob', 'mpg', 'mp4', '3gp',
                  '3g2', 'mkv', 'm4v', 'rm', 'rmvb', 'mov', 'qt', 'ogg', 'ogv', 'oga', 'mod',
                  'wav', 'flac', 'ape', 'alac', 'wv', 'mp3', 'm4a', 'aac', 'ogg', 'opus']
            for root, dirs, files in os.walk(walk_path):
                # 有子目录里，把子目录记到redis中
                dirs = [f for f in dirs if not f[0] == '.']
                files = [f for f in files if not f[0] == '.']
                if files and '.DS_Store' not in files and '@eaDir' not in files:
                    # logging.info('root', root.replace(walk_path + '/',''))
                    # logging.info('key', root.replace(directory+'/','').replace('/',':')+':files')
                    temp_file_list = []
                    for temp_file in files:
                        if temp_file.split('.')[-1].lower() not in fm:
                            pass
                        # 配上文件属性
                        else:
                            # logging.info(root + '/' + temp_file)
                            if os.path.exists(root + '/' + temp_file):
                                file_size = round(os.path.getsize(root + '/' + temp_file) / (1024 * 1024 * 1024), 2)
                                md5_name = temp_file
                                uid = hashlib.md5(md5_name.encode()).hexdigest()  # 放在服务器生成uuid
                                file_c_time = os.path.getmtime(root + '/' + temp_file)
                                file_t = [root.replace(directory, '') + '/', temp_file, uid, file_size,
                                          int(file_c_time)]
                                temp_file_list.append(file_t)
                    r.set('media_server:' + root.replace(directory + '/', '').replace('/', ':') + ':files',
                          json.dumps(temp_file_list))
                    # logging.info(temp_file_list)
                # logging.info('$$$$$$$$$')
                dir_temp = []
                if dirs:
                    if '@eaDir' in dirs:
                        dirs.remove('@eaDir')
                    for d in dirs:
                        d_t = [d, int(os.path.getmtime(root + '/' + d))]
                        # logging.info('d_t',d_t)
                        dir_temp.append(d_t)
                    r.set('media_server:' + root.replace(directory + '/', '').replace('/', ':') + ':dirs',
                          json.dumps(dir_temp))

    def walk_sub_dir(self, directory):
        fm = ['swf', 'flv', 'avi', 'wmv', 'asf', 'wmvhd', 'mpeg', 'dat', 'vob', 'mpg', 'mp4', '3gp',
              '3g2', 'mkv', 'm4v', 'rm', 'rmvb', 'mov', 'qt', 'ogg', 'ogv', 'oga', 'mod',
              'wav', 'flac', 'ape', 'alac', 'wv', 'mp3', 'm4a', 'aac', 'ogg', 'opus']
        for root, dirs, files in os.walk(directory):
            # 有子目录里，把子目录记到redis中
            dirs = [f for f in dirs if not f[0] == '.']
            files = [f for f in files if not f[0] == '.']
            if files and '.DS_Store' not in files and '@eaDir' not in files:
                # logging.info('root', root.replace(walk_path + '/',''))
                # logging.info('key', root.replace(directory+'/','').replace('/',':')+':files')
                temp_file_list = []
                for temp_file in files:
                    if temp_file.split('.')[-1].lower() not in fm:
                        pass
                    # 配上文件属性
                    else:
                        # logging.info(root + '/' + temp_file)
                        file_size = round(os.path.getsize(root + '/' + temp_file) / (1024 * 1024 * 1024), 2)
                        md5_name = temp_file
                        uid = hashlib.md5(md5_name.encode()).hexdigest()  # 放在服务器生成uuid
                        file_c_time = os.path.getmtime(root + '/' + temp_file)
                        file_t = [root.replace(web_server_dir, '') + '/', temp_file, uid, file_size, int(file_c_time)]
                        temp_file_list.append(file_t)
                files_key = 'media_server:' + root.replace(web_server_dir + '/', '').replace('/', ':') + ':files'
                # logging.info('files key',directory,files_key)
                r.set(files_key, json.dumps(temp_file_list))
                # logging.info(temp_file_list)
            # logging.info('$$$$$$$$$')
            dir_temp = []
            if dirs:
                for d in dirs:
                    d_t = [d, int(os.path.getmtime(root + '/' + d))]
                    # logging.info('d_t',d_t)
                    dir_temp.append(d_t)
                dirs_key = ('media_server:' + root.replace(web_server_dir, '').replace('/', ':') + ':dirs').replace(
                    '::', ':')
                # logging.info('dirs key', directory, dirs_key)
                r.set(dirs_key, json.dumps(dir_temp))


class FileEventHandler(FileSystemEventHandler):

    def update(self, walk_sub_dir, action='scan'):
        bobo_server = bobo_server_main()
        dir_name = walk_sub_dir.replace(str(web_server_dir) + '/', '').replace('/', ':')
        data_new = r.keys(pattern='media_server:' + dir_name + ':dirs')
        for item in data_new:
            r.delete(item)
        data_new = r.keys(pattern='media_server:' + dir_name + ':files')
        for item in data_new:
            r.delete(item)
        # bobo_server.scan(web_server_dir)
        if action == 'scan':
            bobo_server.walk_sub_dir(walk_sub_dir)

    def on_moved(self, event):
        if os.path.isdir(event.src_path):
            self.update(event.src_path, 'del')

    def on_modified(self, event):
        if os.path.isdir(event.src_path):
            if str(event.src_path) != web_server_dir:
                temp_dir = event.src_path
                time.sleep(1)
                if temp_dir:
                    logging.info('category changed %s' % temp_dir)
                    self.update(temp_dir)


if __name__ == "__main__":
    logging.info('Initialing，scan all categories')
    # 创建初始目录
    try:
        for item in dirs:
            temp_dir = web_server_dir + "/" + item
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
    except:
        pass
    bobo_server = bobo_server_main()
    bobo_server.scan(web_server_dir)
    time.sleep(10)
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, web_server_dir, recursive=True)
    observer.start()
    logging.info('observer started on %s' % web_server_dir)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
