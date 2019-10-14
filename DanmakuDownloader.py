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

optlist, args = gnu_getopt(sys.argv[1:],'i:',['insert'])

for m in range(0,len(optlist)):
    if str(optlist[m][0]) == str('-i'):
        insertdanmakupath = optlist[m][1]
        if 'insertdanmakupath' in dir() and os.path.exists(insertdanmakupath) and os.path.isdir(insertdanmakupath):
            insertdanmaku = 1

def search():
    global anime
    anime = input('番名?\n')
    if not anime:
        print('不说算了')
        sys.exit()

if len(args) is 0:
    search()
else:
    for k in range(0,len(args)):
        if k is 0:
            anime = args[k]
        else:
            anime = anime+' '+args[k]

getepisode = "https://api.acplay.net/api/v2/search/episodes?anime="
downloadpath = "/sdcard/danmaku/"
subtitlepath = "/storage/emulated/0/Subtitles/"

def get():
    global response,dict
    response = requests.get( getepisode + anime ).text
    dict = json.loads(response)

get()

def notempty():
    if not dict['animes']:
        print('404')
        search()
        get()
        notempty()

notempty()

animetitle = 'nill'
episodes = 'null'
def animelistselector():
    if not len(dict['animes']) is 1:
        for l in range(len(dict['animes'])):
            print(str(l)+'.'+dict['animes'][l]['animeTitle'])
        animelistnumber = input('哪个? ')
        if animelistnumber.isdigit() and int(animelistnumber) in range(len(dict['animes'])):
            global animetitle,episodes
            animetitle = dict['animes'][int(animelistnumber)]['animeTitle']
            episodes = dict['animes'][int(animelistnumber)]['episodes']
            if input('是 '+animetitle+' ? [y/N] ') is 'y':
                pass
            else:
                animelistselector()
        else:
            print('不说算了')
            sys.exit()
    else:
        animetitle = dict['animes'][0]['animeTitle']
        episodes = dict['animes'][0]['episodes']
        if input('是 '+animetitle+' ? [y/N] ') is 'y':
            pass
        else:
            print('404')
            search()
            get()
            animelistselector()

animelistselector()

episode_count = len(episodes)

def downloaddanmaku(epid,eptitle,numberinlist):
    danmaku = requests.get( "https://api.acplay.net/api/v2/comment/"+str(epid)+"?withRelated=true" ).text
    dmdict = json.loads(danmaku)
    if dmdict['count'] > 0 :
        if 'insertdanmaku' in globals() and insertdanmaku is 1:
            #print(将 插入 )
            if not os.path.exists(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak'):
                shutil.copy2(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml', insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak')
            else:
                shutil.copy2(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml.bak', insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml')
            orixml = ET.parse(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml')
            root = orixml.getroot()
        else:
            print('在下 '+eptitle)
            root = ET.Element('i')
        for j in dmdict['comments']:
            d = ET.SubElement(root, 'd')
            d.text = j['m']
            splitedp = re.split(',',j['p'])
            if os.path.exists('danmaku2ass.py') and os.path.isfile('danmaku2ass.py'):
                splitedp[3] = '0'
            splitedp.insert(2,'25')
            splitedp.extend(['0','0','0'])
            d.set('p',",".join(splitedp))
        xml = '<?xml version="1.0" encoding="UTF-8"?>'+ET.tostring(root,'utf-8').decode('utf-8')
        if 'insertdanmaku' in globals() and insertdanmaku is 1:
            open(insertdanmakupath+'/'+str(numberinlist)+'/danmaku.xml','w').write(xml)
        else:
            if not os.path.exists(downloadpath+animetitle.replace('/','\\')):
                os.makedirs(downloadpath+animetitle.replace('/','\\'))
            open(downloadpath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.xml','w').write(xml)
            if os.path.exists('danmaku2ass.py') and os.path.isfile('danmaku2ass.py'):
                if not os.path.exists(subtitlepath+animetitle.replace('/','\\')):
                    os.makedirs(subtitlepath+animetitle.replace('/','\\'))
                os.system('python danmaku2ass.py -s 3840x2160 -fs 100 -dm 30 -ds 30 -o '+'\"'+subtitlepath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.ass'+'\" \"'+downloadpath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.xml'+'\"')
    else:
        print('跳过 '+eptitle)

for i in range(episode_count):
    downloaddanmaku(episodes[i]['episodeId'],episodes[i]['episodeTitle'],i+1)

print(animetitle+' 下好了')
