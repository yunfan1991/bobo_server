import os, subprocess, datetime, time
import schedule

# start set db
from sqlalchemy import create_engine

db_name = '/data/convert.db'
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

# print('is db?',os.path.exists(db_name))
if not os.path.exists(db_name):
    Base.metadata.create_all(engine)
    work = Work(is_scan=0, is_convert=0)
    db.add(work)
    db.commit()

# db set ok

work_dir = '/media/'


class Easy():
    def __init__(self):
        self.scanning = False
        self.is_converting = False

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
            if file is None:
                if self.if_need_to_convert(file_name):
                    need_to_convert.append({'input': file_name})
        # print(need_to_convert)
        # 写入数据库
        for item_dict in need_to_convert:
            # item is a dictionary
            file = db.query(Files).filter_by(input=item_dict['input']).first()
            if not file:
                add_file = Files(**item_dict)
                db.add(add_file)
                db.commit()
                # print(item_dict['input'], ' add ok!')
            else:
                pass
                # print('skip ', item_dict)

    def find_all_videos(self, directory):
        fm = ('flv', 'avi', 'wmv', 'asf', 'wmvhd', 'mpeg', 'dat', 'vob', 'mpg', 'mp4', '3gp',
              '3g2', 'mkv', 'm4v', 'rm', 'rmvb', 'mov', 'webm')
        temp_file_list = []
        for root, dirs, files in os.walk(directory):
            # print(files)
            files = [f for f in files if not f[0] == '.']
            for item in files:
                if item.lower().endswith(fm):
                    temp_file_list.append(root + '/' + item)
        return temp_file_list

    def if_need_to_convert(self, file_address, code="utf8"):
        #如果库里已经有了，跳过
        cmd = "ffprobe -print_format json -show_format -i '%s'" % file_address
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:
                out_info = line.decode(code, 'ignore')
                # print(out_info)
                if out_info:
                    if '"format_name"' in out_info:
                        temp = out_info.split(':')[-1].strip()
                        # print('temp', temp)
                        if 'mp4' in temp:
                            return False
        return True

    def get_media_info(self, file_address):
        self.__external_cmd("ffprobe -print_format json -show_format -i '%s'" % file_address)

    def convert_to_db_format(self, input):
        base_name = os.path.basename(input)
        # print('base_name', base_name)
        output = input.replace(os.path.splitext(base_name)[1], '_easy2mp4.com.mp4')
        if input == output:
            output = input.replace(os.path.splitext(base_name)[1], '_easy2mp4.com_new.mp4')
        return {'input': input}

    def convert_to_mp4(self, input_name, is_delete=False, code="utf8"):
        file = db.query(Files).filter_by(input=input_name).first()
        base_name = os.path.basename(input_name)
        # print('base_name', base_name)
        output = input_name.replace(os.path.splitext(base_name)[1], '_easy2mp4.com.mp4')
        if input_name == output:
            output = input_name.replace(os.path.splitext(base_name)[1], '_easy2mp4.com_new.mp4')
        # print("output", output)
        # return True
        if file.is_fault < 2:
            try:
                file.start_time = datetime.datetime.now()
                db.commit()
                cmd = "ffmpeg -i '%s' '%s'  -y" % (input_name, output)
                process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
                while process.poll() is None:
                    line = process.stdout.readline()
                    line = line.strip()
                    if line:
                        out_info = line.decode(code, 'ignore')
                        if out_info:
                            # print(out_info)
                            if 'Qavg:' in out_info:
                                # 转换成功状态写入数据
                                file.end_time = datetime.datetime.now()
                                file.is_ok = 1
                                # 确认修改
                                db.commit()
                                if is_delete:
                                    # 删除源文件
                                    os.remove(input_name)
                                print('convert ok... ', input_name)
                                time.sleep(30)
                                return True
            except Exception as e:
                #
                file.is_fault = file.is_fault + 1
                db.commit()

        return False

    @staticmethod
    def __external_cmd(cmd, code="utf8"):
        print(cmd)
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:

                out_info = line.decode(code, 'ignore')
                if ' time' in out_info:
                    print('注意，开始转换了', out_info)
                else:
                    print(out_info)

    def walk_sub_dir(self, directory):
        pass


def job_scan(temp_dir=None):
    print("I'm scanning...")
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
            print('scan finish')
            work_obj.is_scan = 0
            db.commit()
        except:
            work_obj.is_scan = 0
            db.commit()


def job_convert():
    print("I'm converting...")
    work_obj = db.query(Work).filter_by(id=1).first()
    easy = Easy()
    if work_obj.is_convert == 0:
        files = easy.get_need_to_convert()
        if files:
            try:
                work_obj.is_convert = 1
                db.commit()
                for item in files:
                    print('start to convert... ', item.input)
                    easy.convert_to_mp4(item.input, is_delete=True)
                print('convert finish')
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
                        print('目录改动', temp_dir)
                        # time.sleep()
                        job_scan(temp_dir)


if __name__ == '__main__':
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
        print('observer started at ', work_dir, datetime.datetime.now())
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
