# DanmakuDownloader

从弹弹play批量下载弹幕  
~~弹弹play的安卓端不支持批量弹幕下载，于是就有了了这个脚本~~  
~~代码就别看了，写的很烂，能用就行~~

# 使用方法

```
python DanmakuDownloader.py <番剧名>
```
或
```
python DanmakuDownloader.py
```
如果```danmaku2ass.py```存在，将自动同时保存弹幕为ass字幕  

如果```bcc2ass.py```存在，将自动在下载 bilibili cc 字幕时保存字幕为 srt 字幕  

使用```-i <视频路径>```可将弹幕插入到视频中

使用```-i <视频路径> -r```可还原被插入的弹幕文件

使用插入模式时可以不指定番剧名称，脚本会自动读取被插入番剧的标题

使用```-b/c <av号>```可以下载bilibili弹幕/ cc 字幕

# 依赖

```python3
import requests #访问api
import json #解析弹弹play弹幕
try:
    import xml.etree.cElementTree as ET #解析bilibili弹幕
except ImportError:
    import xml.etree.ElementTree as ET
import re #文本替换
import os #路径检查
import sys #解析参数
from getopt import gnu_getopt #同上
import shutil #操作文件
from copy import deepcopy #复制变量
import threading #多线程
from opencc import OpenCC #番剧标题转简体，方便弹弹play搜索
```

# TODO
- [x] 弹幕插入视频
- [x] 弹幕插入番剧
- [x] 跳过不存在的ep
- [x] 名称匹配模式
- [x] 如果名称匹配失败启用id匹配
- [x] id匹配失败用手动匹配
- [x] 如果没有番剧名称读取entry.json获取番剧名称
- [x] 不区分大小写
- [x] 多线程下载
- [x] 还原被插入的弹幕
- [x] 插入模式弹幕去重
- [x] 重写逻辑部分
- [x] bilibili av弹幕下载
- [x] bilibili md弹幕下载
- [x] bilibili ss弹幕下载
- [x] bilibili ep弹幕下载
- [ ] bilibili弹幕插入
- [ ] 全弹幕装填
- [ ] 从搜索到的多部番剧批量下载
- [ ] 从番剧名称列表文件批量下载
