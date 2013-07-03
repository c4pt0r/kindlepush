#!/usr/bin/env python
#encoding=utf-8
import os
import urllib2, urllib
import smtplib,mimetypes
from ConfigParser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
import redis

#smtp info
smtp_user = None
smtp_pass = None
smtp_host = None
smtp_port = 25

#kindle info
kindle_account = None

#diffbot api
diffbot_url = "http://www.diffbot.com/api/article?token=9c56b2167b47042697870229163118e5&url="

def get_text_of_link(url):
    fp = urllib2.urlopen(diffbot_url + urllib.quote(url))
    content = fp.read()
    p = json.loads(content)
    return p

def load_config(config_file):
    global smtp_host, smtp_pass, smtp_user, smtp_port, kindle_account
    cf = ConfigParser()
    cf.read(config_file)
    try:
        smtp_user = cf.get("smtp", "user")
        smtp_pass = cf.get("smtp", "password")
        smtp_host = cf.get("smtp", "host")
        #kindle_account = cf.get("kindle", "user")
    except:
        print "load config error"

def send_to_kindle(to, title, content):
    smtp = smtplib.SMTP()
    smtp.connect(smtp_host)
    smtp.login(smtp_user, smtp_pass)

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = 'kindle push email'
    txt = MIMEText("from c4pt0r")
    msg.attach(txt)

    doc = MIMEText(content, 'plain', 'utf-8')
    doc['Content-Type'] = 'application/octet-stream'
    doc.add_header('Content-Disposition', 'attachment', filename = title + '.txt')
    msg.attach(doc)
    smtp.sendmail(smtp_user, to , msg.as_string())

load_config("./config")
#get_text_of_link("http://www.douban.com/group/topic/27252494/")
#send_to_kindle("c4pt0r@kindle.com","save to kindle", "hello world")
if __name__ == '__main__':
    r = redis.Redis("localhost", port = 6379, db = 0)
    while True:
        _, request = r.brpop("push_tasks")
        request = json.loads(request)
        print 'new task!', request
        t = get_text_of_link(request['url'])
        if request['title'] == '@':
            title = t['title']
        else:
            title = request['title']
        content = t['text']
        send_to_kindle(request['sendto'], title, content)
        print 'done'
        print '---------------'

