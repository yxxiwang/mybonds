#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time
import redis
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA   
 
from mybonds.apps import *

REDIS_HOST = 'localhost'
REDIS_PORT = 6379 
REDIS_EXPIRETIME = 186400
DOC_EXPIRETIME = 86400*7
KEY_UPTIME = 1800
QUANTITY = 1500
QUANTITY_DURATION = 300
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
rdoc = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)
 
def sendemail(content, rcv_email,title=""):
    from django.core.mail import send_mail
    print "================sendemail============================"
    import smtplib, mimetypes
    from smtplib import SMTPException
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.Header import Header
    from email.mime.image import MIMEImage
    sender = 'admin@zhijixing.com'
#     sender = '蓝海资讯'
    if rcv_email == "":
        rcv_email = 'yxxiwang@gmail.com'
    receivers = [rcv_email]

    msg = MIMEMultipart()
    msg['From'] = "灯塔阅读"
    msg['To'] = rcv_email
    if title!="":
        msg['Subject'] = Header(title, charset='UTF-8')  # 中文主题 
    else:
        msg['Subject'] = Header('欢迎来到指极星', charset='UTF-8')  # 中文主题 
        
    txt = MIMEText(content, _subtype='html', _charset='UTF-8') 
#    txt = MIMEText(content, _subtype='plain', _charset='UTF-8') 
    # 添加html的邮件内容
    # txt = MIMEText("<a href='http://blog.plotcup.com'>Chronos的博客</a>", _subtype='html',  _charset='UTF-8')
#
    msg.attach(txt)
#    msg.attach(urltxt)
#    message = "\r\n".join([
#      "From: zhijixing2012lsw@gmail.com",
#      "To: yxxiwang@gmail.com",
#      "Subject: Just a message,这是一封测试邮件".decode("utf8"),
#      "",
#      "hi,我是测试邮件".decode("utf8"),
#      ])
    try:
#       message = MIMEText(message,_subtype='plain',_charset='gb2312')
       smtpObj = smtplib.SMTP('smtp.gmail.com')
       smtpObj.ehlo()
       smtpObj.starttls()
       smtpObj.login('admin@zhijixing.com', 'software91') 
       smtpObj.sendmail(sender, receivers, msg.as_string())      
       print "Successfully sent email"
       return 0
    except SMTPException:
       print "Error: unable to send email"
       traceback.print_exc()
       return 8
    else:
       pass
#        print "sent email again.."
#        smtpObj.sendmail(sender, receivers, msg.as_string())
    finally:
       smtpObj.quit() 
        
    return 8

def timeElaspe(create_time, real=False):
    elaspestr = ""
    create_time = int(create_time)
    if create_time == 0:
        return "历史旧闻".decode("utf8")
    current_time = time.time()
    if real:  # 如果传入的create_time 是自然生成,
        elaspe = int(current_time - create_time)
    else:  # 如果传入的create_time是 取自后台返回的结果
        elaspe = int(current_time - create_time / 1000)
    daybefore = int(elaspe / 86400)
    if daybefore == 0:
        hourbefore = int(elaspe / 3600)
        if hourbefore == 0:
            minbefore = int(elaspe / 60)
            elaspestr = str(minbefore) + "分钟前"
        else:
            elaspestr = str(hourbefore) + "小时前"
    else:
        elaspestr = str(daybefore) + "天前"
    return elaspestr.decode("utf8")

def getDataByUrl(urlstr,isservice=False):
    start = time.clock()
    udata = loadFromUrl(urlstr) 
    urlstop = time.clock()  
    diff = urlstop - start  
    print "loadFromUrl(%s) has taken %s" % (urlstr,str(diff))
    docs = []
    if udata.has_key("docs"):
        for doc in udata["docs"]:
            if doc is None:
                continue
            if doc["validTime"]=="false" or not doc["validTime"]:
                continue
#            doc["id"] = getHashid(doc["url"])
            doc["docid"] = getHashid(doc["url"])
            doc["title"] = doc["title"].replace(" ","")
            doc["tx"] = doc["text"].replace(" ","")
            doc["text"] = subDocText(doc["text"])
            doc["copyNum"] = str(doc["copyNum"])
            doc["validTime"] = str(doc["validTime"])
            doc["tms"]=str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"]) 
            docs.append(doc)
        udata["docs"] = docs  
        udata["total"] = str(len(udata["docs"]) )
    else:
        udata["total"] = "0"
        udata["docs"] = []
    return udata
    
def log_typer(request, act, obj):
    quantity = 0 
    client_address = request.META['REMOTE_ADDR']
#    print "client_address===:" + client_address
    quantity = r.incr("quantity:" + client_address, 1)
    if quantity > QUANTITY:
        return quantity
    r.expire("quantity:" + client_address, QUANTITY_DURATION)
    username = getUserName(request)
    logobj = {}
    logobj["usr"] = username
    logobj["ip"] = client_address
    logobj["act"] = act
    logobj["o"] = obj
    logobj["url"] = request.get_full_path()
    logobj["tms"]=time.time()
    r.zadd("log", time.time(), json.dumps(logobj))
    r.hset("usrlst", username, json.dumps(logobj))
    return quantity
    
def getFullDocByUrl(urlstr):
    start = time.clock()
    udata = loadFromUrl(urlstr) 
    urlstop = time.clock()  
    diff = urlstop - start  
    print "loadFromUrl(%s) has taken %s" % (urlstr,str(diff))
    docs = []
    if udata.has_key("docs"):
        for doc in udata["docs"]:
            if doc is None:
                continue
#             if doc["validTime"]=="false" or not doc["validTime"]:
#                 continue 
            doc.pop("urls")
            doc.pop("relatedDocs")
            doc["docid"] = getHashid(doc["url"])
            doc["title"] = doc["title"].replace(" ","") 
            doc["copyNum"] = str(doc["copyNum"])
            doc["validTime"] = str(doc["validTime"])
            doc["tms"]=str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"]) 
            docs.append(doc)
        udata["docs"] = docs  
        udata["total"] = str(len(udata["docs"]) )
        return doc
    else:
        udata["total"] = "0"
        udata["docs"] = []
    return {}

def subDocText(s):
#    us=unicode(s,"utf8")
#    return s
    if s =="":
        return s
    s = s.replace(" ", "")
#    .replace(",", "，".decode("utf8"))
    us=to_unicode_or_bust(s)
    lc=us[-1]
    dot="。".decode("utf8")
    comma = "，".decode("utf8")
    ellipsis=" ......".decode("utf8")
    if lc == dot or lc ==".": #从尾部判断，如果最后一个字符是"。"或者"." 则返回原始文本
        return s
    else:#否则开始进行截取
        slst=us.split(dot)
        if len(slst[-1]) <55:#如果最后一段在"。"之后文本长度小于35,则截断之
            return dot.join(slst[0:-1]+[""]).encode("utf8")
        else:#如果 最后一段文字数大于35个，则从尾部开始，截断到最近一个标点符合，包括，
            clst=slst[-1].split(comma)
            return (dot.join(slst[0:-1]+[""])+comma.join(clst[0:-1]+[""] ) ).encode("utf8")
    return s

def getchannelByid(beaconusr,beaconid): 
    return r.hget("bmk:" + beaconusr + ":" + beaconid,"ttl") 
    # if r.exists("bmk:" + beaconusr + ":" + beaconid) else ""

def pushQueue(qtype, username, otype, tag=None, similarid=None,urlstr=None):
#    if isinstance(username, unicode): 
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username, otype)
#    else:
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username.decode("utf8"), otype)
    qobj = {}
    qobj["usr"] = username
    qobj["o"] = otype
    qobj["tms"] = time.time()
    qobj["type"] = qtype 
#     if qtype in ["tag", "navtag"]:
#         if isinstance(tag, unicode): 
#             urlstr = "http://www.gxdx168.com/research/svc?u=%s&o=%s&tag=%s" % (username, getOtype(otype), tag)
#         else:
#             urlstr = "http://http://www.gxdx168.com.com/research/svc?u=%s&o=%s&tag=%s" % (username, getOtype(otype), tag.decode("utf8"))
#         qobj[qtype] = tag 
#     elif qtype in ["ppl", "rdd", "rcm", "nav"]:
#         urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&o=" + getOtype(otype)
    if qtype == "read":
        urlstr = "http://www.gxdx168.com/research?u=" + username + "&likeid=" + similarid
    elif qtype == "beacon":
        urlstr = "http://www.gxdx168.com/research/svc?channelid=getchannel(%s)" % (tag)
        qobj[qtype] = tag 
    elif qtype == "sendemail": 
        qobj["docid"] = similarid
        qobj["email"] = tag 
#         qobj[qtype] = tag
    elif qtype == "removedoc":
        urlstr="http://www.gxdx168.com/research/svc?u="+tag+"&o=2&likeid=-%s" %(similarid)
        qobj["docid"] = similarid
        qobj[qtype] = tag 

    qobj["url"] = urlstr
    qobj["id"] = getHashid(urlstr)
    r.lpush("queue:" + qtype, json.dumps(qobj))
    

