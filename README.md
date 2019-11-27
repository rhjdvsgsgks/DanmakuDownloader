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

使用```-i/--insert <视频路径>```可将弹幕插入到视频中

# TODO
- [x] 弹幕插入视频
- [x] 弹幕插入番剧
- [x] 跳过不存在的ep
- [x] 名称匹配模式
- [x] 如果名称匹配失败启用id匹配
- [x] id匹配失败用手动匹配
- [ ] 多线程下载
- [ ] 从搜索到的多部番剧批量下载
- [ ] 从番剧名称列表文件批量下载
