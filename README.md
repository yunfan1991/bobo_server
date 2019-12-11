## 欢迎您使用 bobo,适合于家用的媒体服务器

### 一、简介

bobo 是一个私人mp4媒体服务器，适合组织管理下载的mp4文件，尤其适合家庭媒体播放、青少年儿童幼儿视频学习资料的管理。

### 二、第一次运行

#### (1) BOBO安装命令

BOBO运行于Docker之上，如果您有家庭NAS或是Windows/Linux/MacOS电脑，请先安装Docker再运行本软件: 

docker run -d -p 8567:8567 -p 8568:8568 --name bobo -v /Volumes/video:/media -v /data/config:/data yunfan1976/bobo_server

其中 /Volumes/video 替换为本地视频目录
/data/config替换成一个本地目录，用来存放数据库文件

#### (2) 群晖&威联通安装BOBO
##### 群晖可手动安装Docker
群晖docker安装包地址
https://usdl.synology.com/download/Package/spk/Docker/

#### (3) 群晖&威联通安装BOBO
群晖NAS安装BOBO_SERVER视频教程
B站
https://www.bilibili.com/video/av77407158

#### (4) windows下的安装
4.1 安装python3,请于 https://python.org 下载最新python for windows安装包并安装

4.2 安装docker，请于 https://www.docker.com 下载安装docker

4.3 运行bobo安装命令，例

docker run -d -p 8567:8567 -p 8568:8568 --name bobo -v E:\video:/media -v E:\video\data:/data yunfan1976/bobo_server

##### 4.4 安装windows下的文件变化监控软件

4.4.1 中国用户 pip install docker-windows-volume-watcher -i https://mirrors.aliyun.com/pypi/simple

4.4.2 海外用户 pip install docker-windows-volume-watcher 

4.4.3 在windows命令行下运行 docker-volume-watcher bobo E:\video --debounce 0.1


#### (5) linux下的安装，以ubuntu/debian为例
4.1 安装docker，sudo apt install docker.io

4.2 运行bobo安装命令，例

docker run -d -p 8567:8567 -p 8568:8568 --name bobo -v /home/video:/media -v /home/video/data:/data yunfan1976/bobo_server



### 三、本地视频目录凡例： 

电影 movie

剧集 tv

动画 cartoon

综艺 show

MTV mtv

音频 audio

纪录片 doc

专辑 special

##### 孩子学习专用目录 study

### 四、第一次操作后的操作

停止 docker stop bobo

运行 docker start bobo

重启 docker restart bobo

删除 docker rm bobo

### 五、浏览器操作 

成功运行后，打开浏览器，

输入 http://你的IP地址:8568，

初次运行应设置PIN CODE

默认PIN CODE 9999，具有全部观看权限

学习PIN CODE 1234，仅可观看study目录


### 六、格式转换
#### 注意，bobo将会把所有不支持通过网页播放的视频格式转换为mp4格式
##### 如果您不需要转换，请在媒体文件夹根目录放置一个空的 noconvert.txt 文件


### 七、字幕支持

bobo 当前仅支持.srt格式字幕，请将字幕格式设置为 文件名.srt 或 文件名.en.srt(英文字幕) 或 文件名.zh.srt(中文字幕)

# **** For English ***

## Welcome to bobo, a media server for home

### I. Introduction

bobo is a private mp4 media server, suitable for organization and management of downloaded mp4 files, especially suitable for home media playback, video learning materials management for children and young children.

### Second, first run

#### (1) BOBO installation command

BOBO runs on Docker. If you have a home NAS or Windows / Linux / MacOS computer, please install Docker before running this software:

docker run -d -p 8567: 8567 -p 8568: 8568 --name bobo -v / Volumes / video: / media -v / data / config: / data yunfan1976 / bobo_server

Where / Volumes / video is replaced with the local video directory
/ data / config replaced with a local directory for database files

#### (2) Synology & QNAP installed BOBO
##### Synology can manually install Docker
Synology docker installation package address
https://usdl.synology.com/download/Package/spk/Docker/

#### (3) Synology & QNAP installed BOBO
Synology NAS install BOBO_SERVER video tutorial
Station B
https://www.bilibili.com/video/av77407158

#### (4) Installation under windows
4.1 Install python3, please download the latest python for windows installation package at https://python.org and install

4.2 Install docker, please download and install docker at https://www.docker.com

4.3 Run bobo installation command, for example

docker run -d -p 8567: 8567 -p 8568: 8568 --name bobo -v E: \ video: / media -v E: \ video \ data: / data yunfan1976 / bobo_server

##### 4.4 Install file change monitoring software under windows

4.4.1 Chinese users pip install docker-windows-volume-watcher -i https://mirrors.aliyun.com/pypi/simple

4.4.2 Overseas users pip install docker-windows-volume-watcher

4.4.3 Run docker-volume-watcher bobo E: \ video --debounce 0.1 under windows command line


#### (5) Linux installation, using ubuntu / debian as an example
4.1 Install docker, sudo apt install docker.io

4.2 Run bobo installation command, for example

docker run -d -p 8567: 8567 -p 8568: 8568 --name bobo -v / home / video: / media -v / home / video / data: / data yunfan1976 / bobo_server



### Third, the local video directory examples:

Movie movie

Episode tv

Cartoon

Variety show

MTV mtv

Audio

Documentary doc

Album special

##### Special catalog for kids study

### Fourth, the operation after the first operation

Stop docker stop bobo

Run docker start bobo

Restart docker restart bobo

Remove docker rm bobo

### V. Browser Operations

After successfully running, open the browser,

Enter http: // your IP address: 8568,

PIN CODE should be set for the first run

Default PIN CODE 9999, with full viewing rights

Learn PIN CODE 1234, you can only watch the study directory


### Six, format conversion
#### Note that bobo will convert all video formats that are not supported by web pages to mp4
##### If you do not need to convert, place an empty noconvert.txt file in the root folder of the media folder


### 七 、 Subtitle support

bobo currently only supports .srt subtitles, please set the subtitle format to file name.srt or file name.en.srt (English subtitles) or file name.zh.srt (Chinese subtitles)