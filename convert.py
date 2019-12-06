import os, subprocess, datetime, time
import schedule, re

# start set db
from sqlalchemy import create_engine

db_name = '/data/convert.db'
# db_name = 'convert.db'

# work_dir = '/Users/lin/Movies'
work_dir = '/media/'

import logging

logging.basicConfig(filename=work_dir + 'mp4_convert.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db_uri = "sqlite:///" + db_name + "?check_same_thread=False"
engine = create_engine(db_uri)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.orm import sessionmaker
from watchdog.observers import Observer
from watchdog.events import *

Base = declarative_base()


class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    input = Column(String)
    is_ok = Column(Integer, default=0)
    is_fault = Column(Integer, default=0)
    add_time = Column(DATETIME, default=datetime.datetime.now())
    start_time = Column(DATETIME)
    end_time = Column(DATETIME)


class Work(Base):
    __tablename__ = 'work'
    id = Column(Integer, primary_key=True)
    is_scan = Column(Integer, default=0)
    is_convert = Column(Integer, default=0)
    scan_start_time = Column(DATETIME)
    convert_start_time = Column(DATETIME)


Session = sessionmaker(bind=engine)
db = Session()

# logging.info('is db?',os.path.exists(db_name))
if not os.path.exists(db_name):
    Base.metadata.create_all(engine)
    work = Work(is_scan=0, is_convert=0)
    db.add(work)
    db.commit()


# db set ok


class Easy():
    def __init__(self):
        self.fm = ('flv', 'avi', 'wmv', 'asf', 'wmvhd', 'mpeg', 'dat', 'vob', 'mpg', 'mp4', '3gp',
                   '3g2', 'mkv', 'm4v', 'rm', 'rmvb', 'mov', 'webm')

    def get_need_to_convert(self):
        file_list = db.query(Files).filter_by(is_ok=0)
        if file_list:
            return file_list
        else:
            return False

    def scan_to_db(self, work_dir):
        files = self.find_all_videos(work_dir)
        need_to_convert = []
        for file_name in files:
            file = db.query(Files).filter_by(input=file_name).first()
            if not file:
                if self.if_need_to_convert(file_name):
                    need_to_convert.append({'input': file_name})
                else:
                    need_to_convert.append({'input': file_name, 'is_ok': 1})
        # logging.info(need_to_convert)
        # 写入数据库
        for item_dict in need_to_convert:
            # item is a dictionary
            file = db.query(Files).filter_by(input=item_dict['input']).first()
            if not file:
                add_file = Files(**item_dict)
                db.add(add_file)
                db.commit()
                # logging.info(item_dict['input'], ' add ok!')
            else:
                pass
                # logging.info('skip ', item_dict)

    def find_all_videos(self, directory):

        temp_file_list = []
        for root, dirs, files in os.walk(directory):
            # logging.info(files)
            files = [f for f in files if not f[0] == '.']
            for item in files:
                if item.lower().endswith(self.fm):
                    temp_file_list.append(root + '/' + item)
        return temp_file_list

    def if_need_to_convert(self, file_address, code="utf8"):
        # 如果库里已经有了，跳过
        cmd = "ffprobe -logging.info_format json -show_format -i '%s'" % file_address
        if "'" in file_address:
            cmd = 'ffprobe -logging.info_format json -show_format -i "%s" ' % file_address
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:
                out_info = line.decode(code, 'ignore')
                # logging.info(out_info)
                if out_info:
                    if '"format_name"' in out_info:
                        temp = out_info.split(':')[-1].strip()
                        # logging.info('temp', temp)
                        if 'mp4' in temp:
                            return False
        return True

    def get_media_info(self, file_address):
        self.__external_cmd("ffprobe -logging.info_format json -show_format -i '%s'" % file_address)

    def convert_to_db_format(self, input):
        base_name = os.path.basename(input)
        # logging.info('base_name', base_name)
        output = input.replace(os.path.splitext(base_name)[1], '_wulibobo.com_convert.mp4')
        if input == output:
            output = input.replace(os.path.splitext(base_name)[1], '_wulibobo.com_convert_new.mp4')
        return {'input': input}

    def convert_to_mp4(self, input_name, is_delete=False, code="utf8"):
        def format(data):
            '''将font标签和style标签全部删除'''
            p = re.compile(r'<font .*?>|</font>|style=\".*?\"')
            ret = p.sub('', data)
            if ret != data:
                return ret
            else:
                return None

        file = db.query(Files).filter_by(input=input_name).first()
        base_name = os.path.basename(input_name)
        # logging.info('base_name', base_name)
        output = input_name.replace(os.path.splitext(base_name)[1], '_wulibobo.com_convert.mp4')
        if input_name == output:
            output = input_name.replace(os.path.splitext(base_name)[1], '_wulibobo.com_convert_new.mp4')
        # logging.info("output", output)
        # return True
        if file.is_fault < 2:
            try:
                logging.warning('{star convert} %s' % input_name)
                file.start_time = datetime.datetime.now()
                db.commit()
                # 若是mkv，取字幕出来
                srt_name = ''
                if input_name.lower().endswith('mkv'):
                    for i in range(6):
                        srt_name = input_name + '.' + str(i) + '.ass'
                        cmd = "ffmpeg -i %s -map 0:s:%s %s" % (input_name, str(i), srt_name)
                        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                   stderr=subprocess.STDOUT)

                cmd = "ffmpeg -i '%s' '%s'  -y" % (input_name, output)
                if "'" in input_name:
                    cmd = 'ffmpeg -i "%s" "%s"  -y' % (input_name, output)
                process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
                while process.poll() is None:
                    line = process.stdout.readline()
                    line = line.strip()
                    if line:
                        out_info = line.decode(code, 'ignore')
                        if out_info:
                            # logging.info(out_info)
                            if 'Qavg:' in out_info:
                                # 转换成功状态写入数据
                                file.end_time = datetime.datetime.now()
                                file.is_ok = 1
                                # 确认修改
                                db.commit()
                                if is_delete:
                                    # 删除源文件
                                    os.remove(input_name)
                                logging.info('convert ok... ', input_name)
                                # 把字幕转换为srt
                                if srt_name:
                                    file_dir = srt_name.replace(srt_name.split('/')[-1], '')
                                    subprocess.Popen('cd ' + file_dir, shell=True, stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.STDOUT)
                                    subprocess.Popen('pysubs2 --to srt *.ass', shell=True, stdin=subprocess.PIPE,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.STDOUT)

                                logging.warning('{end convert} %s' % input_name)
                                time.sleep(30)
                                return True
            except Exception as e:
                #
                file.is_fault = file.is_fault + 1
                db.commit()

        return False

    @staticmethod
    def __external_cmd(cmd, code="utf8"):
        logging.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:

                out_info = line.decode(code, 'ignore')
                if ' time' in out_info:
                    logging.info('注意，开始转换了', out_info)
                else:
                    logging.info(out_info)

    def walk_sub_dir(self, directory):
        pass


def job_scan(temp_dir=None):
    logging.info("{scna start}")
    if not temp_dir:
        temp_dir = work_dir
    easy = Easy()
    # 扫描入库 #_name).first()
    work_obj = db.query(Work).filter_by(id=1).first()
    if work_obj.is_scan == 0:
        work_obj.is_scan = 1
        db.commit()
        try:
            easy.scan_to_db(temp_dir)
            logging.info('scan finish')
            work_obj.is_scan = 0
            db.commit()
        except:
            work_obj.is_scan = 0
            db.commit()
    logging.info("[scna ended]")


def job_convert():
    logging.info("I'm converting...")
    work_obj = db.query(Work).filter_by(id=1).first()
    easy = Easy()
    if work_obj.is_convert == 0:
        files = easy.get_need_to_convert()
        if files:
            try:
                work_obj.is_convert = 1
                db.commit()
                for item in files:
                    logging.info('start to convert... ', item.input)
                    easy.convert_to_mp4(item.input, is_delete=True)
                logging.info('convert finish')
                work_obj.is_convert = 0
                db.commit()
            except:
                work_obj.is_convert = 0
                db.commit()


class FileEventHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if not '.DS_Store' in str(event.src_path):
            if os.path.isdir(event.src_path):
                if str(event.src_path) != work_dir:
                    temp_dir = event.src_path
                    time.sleep(1)
                    if temp_dir:
                        logging.info('目录改动', temp_dir)
                        # time.sleep()
                        job_scan(temp_dir)


if __name__ == '__main__':
    # 加一个判断，根目录有无需转换的，不转换
    if not os.path.exists(work_dir + 'noconvert.txt'):
        work_obj = db.query(Work).filter_by(id=1).first()
        work_obj.is_scan = 0
        work_obj.is_convert = 0
        db.commit()
        # schedule.every().day.at("01:30").do(job_scan)
        schedule.every().day.at("01:00").do(job_convert)
        job_scan()
        time.sleep(6)
        job_convert()

        # schedule.every(10).minutes.do(job)
        # schedule.every().monday.do(job)
        # schedule.every().wednesday.at("13:15").do(job)

        while True:
            schedule.run_pending()
            time.sleep(10)

            observer = Observer()
            event_handler = FileEventHandler()
            observer.schedule(event_handler, work_dir, recursive=True)
            observer.start()
            # logging.info('observer started at ', work_dir, datetime.datetime.now())
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
