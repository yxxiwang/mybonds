#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time,logging
import redis
from pymongo import MongoClient
from pymongo import Connection
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA   
 
from mybonds.apps import * 

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
rdoc = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1) 
# client = MongoClient('localhost', 27017)
# client = MongoClient('localhost', 27017)
connection = Connection() 
mdoc = connection["doc"]
tftxs = mdoc['tftxs']

sysparms_hkey = {
    "REDIS_EXPIRETIME":"redis_expire",
    "DOC_EXPIRETIME":"doc_expire",
    "KEY_UPTIME":"beacon_interval",
    "REMOVE_KEYUPTIME":"beacon_interval_remove",
    "REMOVE_CNT":"beacon_interval_remove_cnt",
    "CHANNEL_NEWS_NUM":"beacon_news_num",
    "QUANTITY":"quantity",
    "QUANTITY_DURATION":"quantity_duration",
    "RETRY_TIMES":"failed_retry_times",
    "BACKEND_DOMAIN":"backend_domain",
    "DOMAIN":"domain",
    "LOGLEVEL":"loglevel",
}

# REDIS_EXPIRETIME = int(r.hget("sysparms", "redis_expire")) if r.hexists("sysparms","redis_expire") else 186400
# DOC_EXPIRETIME = int(r.hget("sysparms", "doc_expire") ) if r.hexists("sysparms","doc_expire") else 86400*2
# KEY_UPTIME = int(r.hget("sysparms", "beacon_interval")) if r.hexists("sysparms","beacon_interval") else 60*15
# # REMOVE_KEYUPTIME = int(r.hget("sysparms", "beacon_interval_remove")) if r.hexists("sysparms","redis_expire") else 60*5
# # REMOVE_CNT = int(r.hget("sysparms", "beacon_interval_remove_cnt")) if r.hexists("sysparms","redis_expire") else 3
# CHANNEL_NEWS_NUM = int(r.hget("sysparms", "beacon_news_num")) if r.hexists("sysparms","beacon_news_num") else 300
# QUANTITY = int(r.hget("sysparms", "quantity")) if r.hexists("sysparms","quantity") else 1500
# QUANTITY_DURATION = int(r.hget("sysparms", "quantity_duration")) if r.hexists("sysparms","quantity_duration") else 300
# RETRY_TIMES = int(r.hget("sysparms", "failed_retry_times")) if r.hexists("sysparms","failed_retry_times") else 3
# BACKEND_DOMAIN = r.hget("sysparms", "backend_domain") if r.hexists("sysparms","backend_domain") else "svc.zhijixing.com"
# DOMAIN = r.hget("sysparms", "domain") if r.hexists("sysparms","domain") else "www.9cloudx.com"
# LOGLEVEL = r.hget("sysparms", "loglevel") if r.hexists("sysparms","loglevel") else "info"

if not r.hexists("sysparms","redis_expire"):
    r.hset("sysparms", "redis_expire",186400) 
    r.hset("sysparms", "doc_expire",86400*2) 
    r.hset("sysparms", "beacon_interval",60*15) 
    r.hset("sysparms", "beacon_news_num",300) 
    r.hset("sysparms", "quantity",1500) 
    r.hset("sysparms", "quantity_duration",300) 
    r.hset("sysparms", "backend_domain","svc.zhijixing.com")
    r.hset("sysparms", "domain","www.9cloudx.com")
    r.hset("sysparms", "loglevel","info")
    
def loginit(LOGLEVEL):
    if LOGLEVEL is None or LOGLEVEL == "" or LOGLEVEL.lower() == "info":
        LOGLEVEL = logging.INFO
    elif LOGLEVEL.lower() == "debug":
        LOGLEVEL = logging.DEBUG
    elif LOGLEVEL.lower() == "error":
        LOGLEVEL = logging.ERROR
    elif LOGLEVEL.lower() == "warning" or LOGLEVEL.lower() == "warn":
        LOGLEVEL = logging.WARN
    # formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
#     formatter = logging.Formatter('[%(levelname)s %(asctime)s %(module)s:%(lineno)d p%(process)d t%(thread)d] - %(message)s')
    formatter = logging.Formatter('[%(levelname)s %(asctime)s %(module)s:%(lineno)d] - %(message)s')
    #     logging.basicConfig(format='%(asctime)s %(message)s',level=logging.WARN)
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()  
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(LOGLEVEL)
    #     logging.basicConfig(format=formatter)
    logger.warn("enter newspubfunc ,log init done.loglevel is %d" % LOGLEVEL)
    return logger

def getsysparm(parstr):
#     REDIS_EXPIRETIME = int(r.hget("sysparms", "redis_expire")) if r.hexists("sysparms","redis_expire") else 186400
    hval = r.hget("sysparms", sysparms_hkey[parstr.rstrip()])
    return int(hval) if  hval.isdigit() else hval

logger = loginit(getsysparm("LOGLEVEL"))   
def sendemail(content, rcv_email,title=""):
    from django.core.mail import send_mail
    logger.info( "================sendemail============================")
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
    msg['From'] = "灯塔资讯".decode("utf8")
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
       logger.info( "Successfully sent email")
       return 0
    except SMTPException:
       logger.exception( "Error: unable to send email")
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
    logger.info( "loadFromUrl(%s) has taken %s" % (urlstr,str(diff)))
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
    if quantity > getsysparm("QUANTITY"):
        return quantity
    r.expire("quantity:" + client_address, getsysparm("QUANTITY_DURATION") )
    username = getUserName(request)
    logobj = {}
    logobj["usr"] = username
    logobj["ip"] = client_address
    logobj["act"] = act
    logobj["o"] = obj
    logobj["url"] = request.get_full_path()
#     logobj["tms"]=time.time()
    logobj["act_tms"] = "%s" % dt.datetime.now()
    logobj["act_tms"] = logobj["act_tms"][0:19]
    r.zadd("log", time.time(), json.dumps(logobj))
    r.hset("usrlst", username, json.dumps(logobj))
    return quantity
    
def getFullDocByUrl(urlstr):
    start = time.clock()
    udata = loadFromUrl(urlstr) 
    urlstop = time.clock()  
    diff = urlstop - start  
    logger.info( "loadFromUrl(%s) has taken %s" % (urlstr,str(diff)))
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
    
def strfilter(istr):
    return istr.replace("&ldquo;","").replace("&rdquo;","").replace("&amp;","&").replace("&#215;","X")
    
def pushQueue(qtype, username, otype, tag=None, similarid=None,urlstr=None):
#    if isinstance(username, unicode): 
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username, otype)
#    else:
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username.decode("utf8"), otype)
    qobj = {}
    qobj["usr"] = username
    qobj["o"] = otype
    qobj["tms"] = "%s" % dt.datetime.now()
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
#         urlstr = "http://www.gxdx168.com/research/svc?channelid=getchannel(%s)" % (tag)
        qobj[qtype] = tag 
    elif qtype == "fulltext":
#         urlstr = "http://www.gxdx168.com/research/svc?channelid=getchannel(%s)" % (tag)
#         qobj[qtype] = tag 
        qobj[qtype] = tag
    elif qtype == "sendemail":
        qobj["docid"] = similarid
        qobj["email"] = tag 
#         qobj[qtype] = tag
    elif qtype == "removedoc":
        urlstr="http://%s/research/svc?u=%s&o=2&likeid=-%s" %(getsysparm("BACKEND_DOMAIN"),tag,similarid)
        qobj["docid"] = similarid
        qobj[qtype] = tag 

    qobj["url"] = urlstr
    qobj["id"] = getHashid(urlstr)
    r.lpush("queue:" + qtype, json.dumps(qobj))
    
def buildHotBoardData(beaconusr, beaconid,start=0,end=-1,isapi=False):
    key = "bmk:" + beaconusr + ":" + beaconid
    logger.info("key is "+key)
    if r.exists(key):
#         refreshBeacon(beaconusr, beaconid)
        pass
    else:
        return {} 
    udata = {}
    docs = [] 
    channels = []
    channelfromtags = []
    doc_lst = r.zrevrange(key + ":doc:tms", start,end)  # 主题文档集合 
#     print doc_lst
    for docid in doc_lst:
        subdocs = [] 
        doc = rdoc.hgetall("doc:" + docid) 
        if doc == {}:
            logger.warning("doc %s info is not exists!" % docid )
            continue
        doc.pop("text")
        doc.pop("copyNum")
#         doc["text"] = subDocText(doc["text"])
        doc["title"] = doc["title"].decode("utf8")+u"\u3000"
#         doc["copyNum"] = str(doc["copyNum"])
        if doc.has_key("popularity"):
            doc["popularity"] = str(doc["popularity"])
        else:
            doc["popularity"] = "0"
        doc["tms"]=str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        subkey = "bmk:doc:"+getHashid(docid)
        logger.info( "subkey is %s ; docid is %s " %(subkey,docid) )
        if r.exists(subkey):
            subdoc_lst = r.zrevrange(subkey + ":doc:tms", 0,3)
            for subdocid in subdoc_lst:
                subdoc= rdoc.hgetall("doc:" + subdocid)
                if subdoc == {}:
                    logger.warning("subdoc %s info is not exists!" % subdocid ) 
                    continue
                subdoc.pop("text")
                subdoc.pop("copyNum")
                subdoc.pop("popularity")
                subdocs.append(subdoc)
                
        doc["subdocs"]=subdocs
        docs.append(doc)
            
    udata["docs"] = docs
    udata["total"] = str(len(udata["docs"]) )
#     r.hset(key, "cnt", len(docs))
    return udata

