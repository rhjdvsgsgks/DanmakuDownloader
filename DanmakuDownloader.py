import requests
import json
from pprint import pprint as pp
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import re
import os
import sys

if len(sys.argv) is 1:
    anime = input('番名?\n')
    if not anime:
        print('不说算了')
        sys.exit()
else:
    for k in range(1,len(sys.argv)):
        if k is 1:
            anime = sys.argv[k]
        else:
            anime = anime+' '+sys.argv[k]

getepisode =  "https://api.acplay.net/api/v2/search/episodes?anime="
downloadpath = "/sdcard/danmakudownload/"

response = requests.get( getepisode + anime ).text

dict = json.loads(response)
if not dict['animes']:
    print('404')
    sys.exit()

animetitle = 'nill'
episodes = 'null'
def animelistselector():
    for l in range(len(dict['animes'])):
        print(str(l)+'.'+dict['animes'][l]['animeTitle'])
    animelistnumber = input('哪个?\n')
    if animelistnumber.isdigit() and int(animelistnumber) in range(len(dict['animes'])):
        global animetitle,episodes
        animetitle = dict['animes'][int(animelistnumber)]['animeTitle']
        episodes = dict['animes'][int(animelistnumber)]['episodes']
        if input('是 '+animetitle+' ?[y/N]\n') is 'y':
            pass
        else:
            animelistselector()
    else:
        print('不说算了')
        sys.exit()

animelistselector()

episode_count = len(episodes)

def downloaddanmaku(epid,eptitle):
    danmaku = requests.get( "https://api.acplay.net/api/v2/comment/"+str(epid)+"?withRelated=true" ).text
    dmdict = json.loads(danmaku)
    root = ET.Element('i')
    for j in dmdict['comments']:
        d = ET.SubElement(root, 'd')
        d.text = j['m']
        splitedp = re.split(',',j['p'])
        splitedp[3] = '0'
        splitedp.insert(2,'25')
        splitedp.extend(['0','0','0'])
        d.set('p',",".join(splitedp))
    if not os.path.exists(downloadpath+animetitle.replace('/','\\')):
        os.makedirs(downloadpath+animetitle.replace('/','\\'))
    xml = '<?xml version="1.0" encoding="utf-8"?>'+ET.tostring(root,'utf-8').decode('utf-8')
    open(downloadpath+animetitle.replace('/','\\')+'/'+eptitle.replace('/','\\')+'.xml','w').write(xml)

for i in range(episode_count):
    print('在下 '+episodes[i]['episodeTitle'])
    downloaddanmaku(episodes[i]['episodeId'],episodes[i]['episodeTitle'])

print(animetitle+' 下好了')
