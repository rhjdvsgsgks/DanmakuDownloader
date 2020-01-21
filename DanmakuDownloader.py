#!/usr/bin/env python3

import requests
import json
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import re
import os
import sys
from getopt import gnu_getopt
import shutil
from copy import deepcopy
import threading
from opencc import OpenCC


def detectargs():
    global args,insertdanmaku,insertdanmakupath,downloadfrombilibili,restoreinsertdanmaku,bilipath
    optlist, args = gnu_getopt(sys.argv[1:],'i:rb:')

    for m in range(len(optlist)):
        if optlist[m][0] == '-i':
            insertdanmakupath = optlist[m][1]
            if 'insertdanmakupath' in globals() and os.path.exists(insertdanmakupath) and os.path.isdir(insertdanmakupath):
                insertdanmaku = True
        if optlist[m][0] == '-b':
            downloadfrombilibili = True
            bilipath = optlist[m][1]

    for m in range(len(optlist)):
        if optlist[m][0] == '-r' and insertdanmaku:
            restoreinsertdanmaku = True


def restore():
    bakexistindir = [os.path.exists(insertdanmakupath+'/'+i+'/danmaku.xml.bak') and os.path.isfile(insertdanmakupath+'/'+i+'/danmaku.xml.bak') for i in os.listdir(insertdanmakupath)]
    if True not in bakexistindir:
        print('没找到 .bak')
        return
    [shutil.move(insertdanmakupath+'/'+i+'/danmaku.xml.bak', insertdanmakupath+'/'+i+'/danmaku.xml') for i in os.listdir(insertdanmakupath) if os.path.exists(insertdanmakupath+'/'+i+'/danmaku.xml.bak') and os.path.isfile(insertdanmakupath+'/'+i+'/danmaku.xml.bak')]


def search():
    global anime
    anime = input('番名?\n')
    if not anime:
        print('不说算了')
        exit()


def getanime():
    global anime
    if len(args) == 0:
        if 'insertdanmaku' in globals() and insertdanmaku is True:
            with open(insertdanmakupath+'/'+os.listdir(insertdanmakupath)[0]+'/entry.json','r') as entryjson:
                entryjsondict = json.load(entryjson)
                anime = OpenCC('t2s').convert(entryjsondict['title'])
        else:
            search()
    else:
        for k in range(len(args)):
            if k == 0:
                anime = args[k]
            else:
                anime = anime+' '+args[k]


downloadpath = "/sdcard/danmaku/"
subtitlepath = "/storage/emulated/0/Subtitles/"


def get():
    global response,dict
    response = requests.get('https://api.acplay.net/api/v2/search/episodes?anime='+anime).text
    dict = json.loads(response)


def notempty():
    if not dict['animes']:
        print('404')
        search()
        get()
        notempty()


def animelistselector():
    if not len(dict['animes']) == 1:
        for l in range(len(dict['animes'])):
            print(str(l)+' '+dict['animes'][l]['animeTitle'])
        animelistnumber = input('哪个? ')
        if animelistnumber.isdigit() and int(animelistnumber) in range(len(dict['animes'])):
            global animetitle,episodes
            animetitle = dict['animes'][int(animelistnumber)]['animeTitle']
            episodes = dict['animes'][int(animelistnumber)]['episodes']
            tempinput = input('是 '+animetitle+' ? [Y/n] ')
            if tempinput == 'y' or tempinput == '':
                pass
            else:
                animelistselector()
        else:
            print('不说算了')
            exit()
    else:
        animetitle = dict['animes'][0]['animeTitle']
        episodes = dict['animes'][0]['episodes']
        tempinput = input('是 '+animetitle+' ? [Y/n] ')
        if tempinput == 'y' or tempinput == '':
            pass
        else:
            print('404')
            search()
            get()
            animelistselector()
    global episode_count
    episode_count = len(episodes)


def reslovbili():
    global cidtitle,animetitle,bilipath
    if bilipath[:2] == 'md':
        #解析md
        media_id = json.loads(requests.get('https://api.bilibili.com/pgc/review/user?media_id='+bilipath[2:]).text)
        section = json.loads(requests.get('https://api.bilibili.com/pgc/web/season/section?season_id='+str(media_id['result']['media']['season_id'])).text)
        avlist = [i['aid' ] for i in section['result']['main_section']['episodes']]
        if False not in [avlist[0] == i for i in avlist]:
            #老番，每p都在一个av里，返回av模式
            bilipath = 'av'+str(avlist[0])
            reslovbili()
            return
        avinfolist = [json.loads(requests.get('https://api.bilibili.com/x/web-interface/view?aid='+str(i)).text)['data'] for i in avlist]
        plist = [i['pages'][0] for i in avinfolist]
        animetitle = media_id['result']['media']['title']
        cidtitle = [[i['cid'] for i in plist],[i['long_title'] for i in section['result']['main_section']['episodes']]]
    elif bilipath[:2] == 'ss':
        #解析ss
        season = json.loads(requests.get('https://api.bilibili.com/pgc/view/web/season?season_id='+bilipath[2:]).text)
        #ss转md
        bilipath = 'md'+str(season['result']['media_id'])
        reslovbili()
    elif bilipath[:2] == 'ep':
        #解析ep
        season = json.loads(requests.get('https://api.bilibili.com/pgc/view/web/season?ep_id='+bilipath[2:]).text)
        #ep转md
        bilipath = 'md'+str(season['result']['media_id'])
        reslovbili()
    elif bilipath[:2] == 'av':
        #解析av
        avinfo = json.loads(requests.get('https://api.bilibili.com/x/web-interface/view?aid='+bilipath[2:]).text)['data']
        plist = avinfo['pages']
        animetitle = avinfo['title']
        cidtitle = [[i['cid'] for i in plist],[i['part'] for i in plist]]
    else:
        print('仅支持av md ss ep')


def downloaddanmaku(epid,eptitle,numberinlist='',ptitle=''):
    danmaku = requests.get( "https://api.acplay.net/api/v2/comment/"+str(epid)+"?withRelated=true" ).text
    dmdict = json.loads(danmaku)
    if dmdict['count'] > 0 :
        if numberinlist != '':
            # 插入弹幕
            if not os.path.exists(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak'):
                # 备份未插入的xml
                shutil.copy2(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml', insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak')
            else:
                # 从备份恢复
                shutil.copy2(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak', insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml')
            orixml = ET.parse(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml')
            root = orixml.getroot()
            remotedanmakufrombilibili = [x for x in dmdict['comments'] if re.split(',',x['p'])[3][:10] == '[BiliBili]']
            localdanmakufromxml = [x.text for x in root.findall('d')]
            #远程b站弹幕+远程非b站弹幕且与本地b站弹幕不重复的弹幕

            def pjoindict(p):
                remotedanmakufrombilibiliwithouttag = deepcopy(remotedanmakufrombilibili)
                for x in remotedanmakufrombilibiliwithouttag:
                    for y in p:
                        x['p'] = y
                return remotedanmakufrombilibiliwithouttag
            dmdict['comments'] = pjoindict([','.join(re.split(',',x['p'])[:3]+[re.split(',',x['p'])[3][10:]]) for x in dmdict['comments'] if x in remotedanmakufrombilibili])+[x for x in dmdict['comments'] if x not in remotedanmakufrombilibili and x['m'] not in localdanmakufromxml]
        else:
            print('在下 '+eptitle)
            root = ET.Element('i')
        for j in dmdict['comments']:
            d = ET.SubElement(root, 'd')
            d.text = j['m']
            splitedp = re.split(',',j['p'])
            if os.path.exists('danmaku2ass.py') and os.path.isfile('danmaku2ass.py') and splitedp[3][0] == '[':
                # danmaku2ass遇到发送者包含非数字内容会出错
                splitedp[3] = '0'
            splitedp.insert(2,'25')
            splitedp.extend(['0','0','0'])
            d.set('p',",".join(splitedp))
        if numberinlist != '':
            # 插入弹幕
            print('从 '+eptitle+' 向 '+ptitle+' 插入了 '+str(len(dmdict['comments']))+' 条弹幕,共 '+str(len(root.findall('d')))+' 条弹幕')
            with open(insertdanmakupath+'/'+str(numberinlist)+'/entry.json','r') as entryjson:
                entryjsondict = json.load(entryjson)
            entryjsondict['danmaku_count'] = len(root.findall('d'))
            with open(insertdanmakupath+'/'+str(numberinlist)+'/entry.json','w') as entryjson:
                json.dump(entryjsondict,entryjson)
        xml = '<?xml version="1.0" encoding="UTF-8"?>'+ET.tostring(root,'utf-8').decode('utf-8')
        if numberinlist != '':
            # 插入弹幕,写回原xml
            open(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml','w').write(xml)
        else:
            if not os.path.exists(downloadpath+animetitle.replace('/','\\')):
                os.makedirs(downloadpath+animetitle.replace('/','\\'))
            open(downloadpath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.xml','w').write(xml)
            if os.path.exists('danmaku2ass.py') and os.path.isfile('danmaku2ass.py'):
                if not os.path.exists(subtitlepath+animetitle.replace('/','\\')):
                    os.makedirs(subtitlepath+animetitle.replace('/','\\'))
                os.system('python danmaku2ass.py -s 3840x2160 -fs 85 -dm 20 -ds 20 -p 103 -o '+'\"'+subtitlepath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.ass'+'\" \"'+downloadpath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.xml'+'\"')
    else:
        print('跳过 '+eptitle)


def bilidownloaddanmaku(cid,part):
    print('在下 '+part)
    response = requests.get('https://comment.bilibili.com/'+str(cid)+'.xml')
    response.encoding = 'utf-8'
    xml = response.text
    if not os.path.exists(downloadpath+animetitle.replace('/','\\')):
        os.makedirs(downloadpath+animetitle.replace('/','\\'))
    open(downloadpath+animetitle.replace('/','\\')+'/'+part.replace('/','\\')+'.xml','w').write(xml)
    if os.path.exists('danmaku2ass.py') and os.path.isfile('danmaku2ass.py'):
        if not os.path.exists(subtitlepath+animetitle.replace('/','\\')):
            os.makedirs(subtitlepath+animetitle.replace('/','\\'))
        os.system('python danmaku2ass.py -s 3840x2160 -fs 85 -dm 20 -ds 20 -p 103 -o '+'\"'+subtitlepath+animetitle.replace('/','\\')+'/'+part.replace('/','\\')+'.ass'+'\" \"'+downloadpath+animetitle.replace('/','\\')+'/'+part.replace('/','\\')+'.xml'+'\"')


def createtasklist():
    global threads
    if 'downloadfrombilibili' in globals() and downloadfrombilibili is True:
        if 'insertdanmaku' in globals() and insertdanmaku is True:
            print('从bilibili插入')
        else:
            print('从bilibili下载')
            threads = [threading.Thread(target=bilidownloaddanmaku,args=[cidtitle[0][i],cidtitle[1][i]]) for i in range(len(cidtitle[0]))]
    else:
        if 'insertdanmaku' in globals() and insertdanmaku is True:
            # 插入弹幕
            entrydirlist = os.listdir(insertdanmakupath)
            epcount = len(entrydirlist)
            indexep = {}
            indextitle = {}
            for n in range(len(entrydirlist)):
                with open(insertdanmakupath+'/'+entrydirlist[n]+'/entry.json','r') as entryjson:
                    entryjsondict = json.load(entryjson)
                if 'avid' in entryjsondict :
                    # 视频
                    indexep[int(entryjsondict['page_data']['page'])],indextitle[int(entryjsondict['page_data']['page'])] = int(entrydirlist[n]),entryjsondict['page_data']['part']
                else:
                    # 番剧
                    indexep[int(entryjsondict['ep']['index'])],indextitle[int(entryjsondict['ep']['index'])] = int(entryjsondict['ep']['episode_id']),entryjsondict['ep']['index_title']
            existep = list(indextitle.keys())
            hasextraep = False
            for p in range(episode_count):
                if episodes[p]['episodeTitle'][0] == 'S':
                    # 判断有附加p
                    hasextraep = True
                    break
            if hasextraep is True:
                # 有附加p,根据每p名称重新排序
                sortedep = ['']*episode_count
                episodesnonumber = deepcopy(episodes)
                for o in range(episode_count):
                    splitedep = re.split(' ',episodesnonumber[o]['episodeTitle'])
                    if len(splitedep) > 1 and splitedep[0][1].isdigit():
                        del splitedep[0]
                        episodesnonumber[o]['episodeTitle'] = ' '.join(splitedep)
                    for p in existep:
                        if episodesnonumber[o]['episodeTitle'].lower() == indextitle[p].lower():
                            sortedep[p-1] = episodes[o]
                            episodes[o] = ''
                if len([x for x in sortedep if x != '']) != epcount:
                    #判断非空位
                    print('有多出来的,使用id匹配')
                    unusedepisodes = [x for x in indextitle if sortedep[x-1] == '']
                    for i in unusedepisodes:
                        tempinput = input(str(i)+' '+indextitle[i]+' 是 '+episodes[i-1]['episodeTitle']+' ? [Y/n] ')
                        if tempinput == 'y' or tempinput == '':
                            sortedep[i-1] = episodes[i-1]
                            episodes[i-1] = ''
                if len([sortedep[x-1] for x in indextitle.keys() if sortedep[x-1] == '']) > 0:
                    #判断在按本地ep排序的episodes中有几个空位
                    print('还是有多的，使用手动匹配')
                    for i in indextitle.keys():
                        if sortedep[i-1] == '':
                            for k in [j for j in range(len(episodes)) if episodes[j] != '']:
                                print(str(k)+' '+episodes[k]['episodeTitle'])
                            selectepisode = int(input(str(i)+' '+indextitle[i]+'是? '))
                            sortedep[i-1] = episodes[selectepisode]
                            episodes[selectepisode] = ''
                threads = [threading.Thread(target=downloaddanmaku,args=[sortedep[i-1]['episodeId'],sortedep[i-1]['episodeTitle'],indexep[i],indextitle[i]]) for i in indexep.keys()]
            else:
                # 没附加p
                threads = [threading.Thread(target=downloaddanmaku,args=[episodes[i-1]['episodeId'],episodes[i-1]['episodeTitle'],indexep[i],indextitle[i]]) for i in indexep.keys()]
        else:
            # 正常下载
            threads = [threading.Thread(target=downloaddanmaku,args=[episodes[i]['episodeId'],episodes[i]['episodeTitle']]) for i in range(episode_count)]


detectargs()
if 'restoreinsertdanmaku' in globals() and restoreinsertdanmaku:
    restore()
else:
    if 'downloadfrombilibili' in globals() and downloadfrombilibili is True:
        #解析b站然后直接创建threads
        reslovbili()
        createtasklist()
    else:
        getanime()
        get()
        notempty()
        animelistselector()
        createtasklist()

    for i in threads:
        i.start()

    for i in threads:
        i.join()

    print(animetitle+' 下好了')
