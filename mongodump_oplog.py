#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import json
import logging
import schedule


## mongodb config
db_host="192.168.0.124"
db_port=27017
db_user="admin"
db_passwd="123456"
db_authdbname="admin"
#路径配置 以斜杠结尾
#mongo_home="Q:/javaProgramFiles/NOSQL/mongodb-win32-x86_64-2012plus-4.2.0/bin/"
#backup_home="Q:/javaProgramFiles/NOSQL/mongodb-win32-x86_64-2012plus-4.2.0/bin/"
mongo_home="/opt/mongodb/mongodb-linux-x86_64-rhel70-4.2.3/bin/"
backup_home="/opt/mongodb/"
backup_gzip="--gzip"
backup_time="03:00"
############### 方法区################

def get_format_time(secs):
	return time.strftime("%Y%m%d%H%M%S",time.localtime(secs))

#读取文件内容
def openfile(path):
    with open(path, 'r') as f:
        return f.read()
#写文件
def writefile(path,content):
    with open(path, 'w') as f:
        f.write(content)
    debug("写入文件内容：%s",content)

#日志初始化
def init_log(logFilename):
    # 判断该目录是否存在
    logPath=os.path.dirname(logFilename)
    isExists = os.path.exists(logPath)
    if not isExists:
        os.makedirs(logPath)
        print("日志目录创建成功:",logPath)

    #''''' Output log to file and console '''
    # Define a Handler and set a format which output to file
    logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，大于此级别的都被输出
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        filename=logFilename,  # log文件名
        filemode='a')  # 写入模式“w”或“a”
    # Define a Handler and set a format which output to console
    console = logging.StreamHandler()  # 定义console handler
    console.setLevel(logging.INFO)  # 定义该handler级别
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # 定义该handler格式
    console.setFormatter(formatter)
    # Create an instance
    logging.getLogger().addHandler(console)  # 实例化添加handler

    # Print information              # 输出日志级别
    # logging.debug('logger debug message')
    # logging.info('logger info message')
    # logging.warning('logger warning message')
    # logging.error('logger error message')
    # logging.critical('logger critical message')
def debug(msg):
    logging.debug(msg)
def debug(msg,arg):
    logging.debug(msg,arg)

#定时调用
def job():
    if not os.path.exists(main_oplog):
        cmd = "%smongodump -h %s:%s --authenticationDatabase %s --authenticationMechanism SCRAM-SHA-1 -u %s -p %s --oplog -o=%s" % (
        mongo_home, db_host, db_port, db_authdbname, db_user, db_passwd, main_backup)
        debug("执行全量备份命令：%s", cmd)
        val = os.system(cmd)
        debug("执行全量备份结果：%s", val)
        return
    # 读取最后增量备份时间
    backup_time_read = "";
    if os.path.exists(next_backup_time):
        next_backup_time_content = openfile(next_backup_time)
        backup_time_read = json.loads(next_backup_time_content)
    else:
        cmd = "%sbsondump %smain_backup/oplog.bson" % (mongo_home, backup_home)
        debug("执行命令：%s", cmd)
        val = os.popen(cmd)
        res = val.read()
        for line in res.splitlines():
            val = line
        debug("返回结果：%s", val)
        bsondump_jsonresult = json.loads(val)
        backup_time_read = bsondump_jsonresult["ts"]
    # 命令行不识别json 需要加斜杠
    bsondump_endtime_query = {"$timestamp": {"t": int(time.time()), "i": 1}}
    #时间提前1秒避免数据丢失，oplog恢复时实际数据不会重复
    backup_time_read["$timestamp"]["t"]=backup_time_read["$timestamp"]["t"] - 1000
    bsondump_query = {"ts": {"$gt": backup_time_read, "$lte": bsondump_endtime_query}}
    bsondump_query = json.dumps(bsondump_query)
    bsondump_query = bsondump_query.replace("\"", "\\\"")
    debug("备份时间查询条件：%s", bsondump_query)
    timestr = time.strftime("%Y%m%d%H%M%S", time.localtime())
    next_backup_home = next_backup + timestr + "/"
    cmd = "%smongodump -h %s:%s --authenticationDatabase %s --authenticationMechanism SCRAM-SHA-1 -u %s -p %s -d local -c oplog.rs -q \"%s\" -o=%s %s" % (
    mongo_home, db_host, db_port, db_authdbname, db_user, db_passwd, bsondump_query, next_backup_home,backup_gzip)
    debug("执行命令：%s", cmd)
    val = os.system(cmd)
    if val == 0:
        # 写入新的文件
        writefile(next_backup_time, json.dumps(bsondump_endtime_query))
        debug("备份完成时间：%s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()));
    else:
        debug("备份失败时间：%s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()));
###############逻辑区################
main_backup=backup_home+"main_backup"
main_oplog=main_backup+"/oplog.bson"
next_backup=backup_home + "next_backup/"
next_backup_time=next_backup+"/next_backup_time.bson"
#日志初始化
init_log(main_backup+"/mongodump.log")
#启动执行
job();
#定时执行
schedule.every().day.at(backup_time).do(job)         # 每天在 03:00 时间点运行 job 函数
#schedule.every(30).seconds.do(job)                  # 每隔 10 分钟运行一次 job 函数
#定时任务
while True:
    schedule.run_pending()   # 运行所有可以运行的任务
    time.sleep(1)



###笔记####
# 1.全库备份 --oplog必须全库不能跟-d参数
# mongodump -h 192.168.0.124:27017 --authenticationDatabase admin --authenticationMechanism SCRAM-SHA-1 -u admin -p 123456 --oplog -o=bkm
# 2.增量备份-读取时间
# bsondump bkm/oplog.bson
#3.增量备份-循环增量备份
# mongodump --uri="mongodb://admin:123456@192.168.0.124:27017,192.168.0.125:27017/local?replicaSet=mongoreplset&authSource=admin" -c oplog.rs -q "{\"ts\":{\"$gt\": {\"$timestamp\": {\"t\": 1582530659, \"i\": 1}}}}"  --gzip -o bkm2

###备注####
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