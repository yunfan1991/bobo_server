### bobo_server Faq 持续更新中
### 1.bobo_server的应用场景
bobo_server 是一个私人mp4媒体服务器，适合组织管理下载的mp4文件，尤其适合家庭媒体播放、青少年儿童、幼儿视频学习资料的管理。

### 2.如何安装bobo_server
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