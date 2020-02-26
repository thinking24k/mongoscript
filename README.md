
# 脚本地址

1. github [https://github.com/thinking24k/mongoscript.git](https://github.com/thinking24k/mongoscript.git)
2. 码云 [https://gitee.com/dawn-a/mongoscript.git](https://gitee.com/dawn-a/mongoscript.git)

# 功能

脚本启动后立即对mongodb数据库进行本地全量备份，获取oplog时间戳，然后每天定时进行增量备份，脚本已内置定时器，只需要把脚本加入开机启动。所有配置都在脚本内更改，脚本支持跨平台。

# 采坑说明
1. Oplog的开启是需要开启副本集才能开启的，所以以上备份策略是针对副本集。
2. 时间戳格式 [mongodb时间戳规范](https://docs.mongodb.com/manual/reference/mongodb-extended-json/#bson.Timestamp)
3. json规范更新需要用“\”转义。如：`{\"ts\":{\"$gt\": {\"$timestamp\": {\"t\": 1582524149, \"i\": 1}}}}`

# 脚本运行环境

使用python3.7.6和 mongo4.2.3

脚本依赖python schedule模块需要执行:
`pip install schedule` 或 `pip3 install schedule`


# 脚本部署步骤
#### Centos7
### 直接运行
1. 命令 `python3 mongodump_oplog.py`

### 后台运行
1. 命令 `nohup python3 -u  mongodump_oplog.py > out.log 2>&1 &`
2. 查看后台 `ps aux |grep python`
3. 删除进程 `kill -9  [进程id]`

### 开机启动
1. 编辑rc.local  
` vim /etc/rc.d/rc.local`
2. 添加开机执行的xx.py文件  
` python3 /opt/mongodb/mongodump_oplog.py`
3. 赋予脚本可执行权限（/opt/mongodb/mongodump_oplog.py是你的脚本路径）  
` chmod +x /opt/mongodb/mongodump_oplog.py`
4. 在centos7中，/etc/rc.d/rc.local的权限被降低了，所以需要执行如下命令赋予其可执行权限  
` chmod +x /etc/rc.d/rc.local`