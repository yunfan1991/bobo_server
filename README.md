## 欢迎您使用 bobo_server,适合于家用的媒体服务器

### 一、简介

bobo_server 是一个私人mp4媒体服务器，适合组织管理下载的mp4文件，尤其适合家庭媒体播放、青少年儿童幼儿视频学习资料的管理。

### 二、第一次运行

BOBO运行于Docker之上，如果您有家庭NAS或是Windows/Linux/MacOS电脑，请先安装Docker再运行本软件: 

docker run -d -p 8567:8567 -p 8568:8568 --name bobo_server -v /Volumes/video:/media -v /data/config:/data yunfan1976/bobo_server

其中 /Volumes/video 替换为本地视频目录

#### 注意，bobo_server将会把所有不支持通过网页播放的视频格式转换为mp4格式
##### 如果您不需要转换，请在媒体文件夹根目录放置一个空的 noconvert.txt 文件

/data/config替换成一个本地目录，用来存放数据库文件

##### 群晖可手动安装Docker
包地址
https://usdl.synology.com/download/Package/spk/Docker/

##### 群晖NAS安装BOBO_SERVER视频教程
B站
https://www.bilibili.com/video/av77407158

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

停止 docker stop bobo_server

运行 docker start bobo_server

### 五、浏览器操作 

成功运行后，打开浏览器，

输入 http://你的IP地址:8568，

初次运行应设置PIN CODE

默认PIN CODE 9999，具有全部观看权限

学习PIN CODE 1234，仅可观看study目录

### 六、字幕支持

bobo_server 当前仅支持.srt格式字幕，请将字幕格式设置为 文件名.en.srt(英文字幕) 或 文件名.chs.srt(中文字幕)

### **** For English ***

First, bobo_server is a private mp4 media server, suitable for organizing and managing downloaded mp4 files, especially suitable for the management of video learning materials for children and children in home media.

Second, the first run

Docker run -d -p 8567:80 -p 8568:8568 --name bobo_server -v /Volumes/video:/media_server -v /data/config:/data yunfan1976/bobo_server

Where /Volumes/video is replaced with a local video directory

/data/config is replaced with a local directory for storing database files

Third, the local video directory example:

movie movie

Episode tv

Animation cartoon

Variety show

MTV mtv

Audio audio

Documentary doc

Album special

Child learning special catalog study

Fourth, the operation after the first operation

Stop docker stop bobo_server

Run docker start bobo_server

V. Browser operation After running successfully, open the browser and enter http://your IP address: 8568. You should set PIN CODE for the first run.

Default PIN CODE 9999 with full viewing rights

Learn PIN CODE 1234, only watch the study directory