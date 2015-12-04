import sopel
import pymysql
import datetime
from urllib.parse import urlparse
from sopel.tools import Identifier
import re
from youtoob import fetch_video_info 
#youtoob is this module slightly renamed: https://github.com/ridelore/willie-modules/blob/master/youtube.py
import soundcloud

def soundcloudtitle(link):
    client = soundcloud.Client(client_id='clientidgoeshere')
    track = client.get('/resolve', url = link, client_id='clientidgoeshere')
    return "{0} - {1}".format(track.user['username'],track.title)


def mysql(name=None, link=None, song=None, sdate=None, action=None):
    connection = pymysql.connect(host='', user='',passwd='', db='',charset='utf8')
    cursor = connection.cursor()
    if action == 'insert':
        sql = "INSERT INTO sotd (name, link, song, sdate) VALUES(%s,%s,%s,%s)"
        cursor.execute(sql, (name, link, song, sdate))
        connection.commit()

    if action == 'select':
        sql = "SELECT * FROM sotd order by id desc limit 0,1"
        cursor.execute(sql)
        res = cursor.fetchone()
        connection.close()
        return res
    connection.close()



@sopel.module.commands('sotd')
@sopel.module.example('.sotd weblink | website for history: weblink')
def sotd(bot, trigger):
    if(trigger.group(2)):
        match = re.match(r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}(youtube|sc0tt|pomf|soundcloud)\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', trigger.group(2), re.I)
        if match:
            name = Identifier(trigger.nick)
            link = match.group(0)
            domain = urlparse(link)
            if(domain.netloc == 'youtu.be' or domain.netloc == 'www.youtu.be'):
                yt = fetch_video_info(bot, domain.path[1:])
                song = yt['title']
            elif(domain.netloc == 'youtube.com' or domain.netloc == 'www.youtube.com'):
                yt = fetch_video_info(bot, domain.query[2:])
                song = yt['title']
            elif(domain.netloc == 'soundcloud.com' or domain.netloc == 'www.soundcloud.com'):
                song = soundcloudtitle(link)
            else:    
                song = ""
            sdate = datetime.datetime.now()
            mysql(name, link, song, sdate,'insert')
            return bot.say("Song saved.")
        else:
            return bot.say("Enter a valid link.")
    else:
        res = mysql(action='select')
        bot.say("Last SotD: {0}".format(res[2]))
