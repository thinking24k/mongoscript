功能

启动后立即对mongodb数据库进行本地全量备份，获取oplog时间戳，然后每天定时进行增量备份，脚本已内置定时器，只需要把脚本加入开机启动。所有配置都在脚本内更改，脚本支持跨平台。

脚本运行环境

使用python3.7.6和 mongo4.2.3

脚本依赖schedule需要执行:
pip install schedule 或 pip3 install schedule


脚本部署步骤
##Centos7
#后台运行
# nohup python3 -u  mongodump_oplog.py > out.log 2>&1 &
#查看后台 ps aux |grep python
#删除进程 kill -9  [进程id]

#开机启动
# vim /etc/rc.d/rc.local
#添加开机执行的xx.py文件
# python3 /opt/mongodb/mongodump_oplog.py
#赋予脚本可执行权限（/opt/mongodb/mongodump_oplog.py是你的脚本路径）
# chmod +x /opt/mongodb/mongodump_oplog.py
#在centos7中，/etc/rc.d/rc.local的权限被降低了，所以需要执行如下命令赋予其可执行权限
# chmod +x /etc/rc.d/rc.local