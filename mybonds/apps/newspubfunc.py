#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string, random
import sys, time, logging
import redis
import re
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
trelate = mdoc['trelate']
ttrack = mdoc['ttrack']
tpopulary = mdoc['tpopulary']
tchannel = mdoc['tchannel']
tchannelpick = mdoc['tchannelpick']
textend = mdoc['textend']

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

if not r.hexists("sysparms", "redis_expire"):
    r.hset("sysparms", "redis_expire", 186400) 
    r.hset("sysparms", "doc_expire", 86400 * 2) 
    r.hset("sysparms", "beacon_interval", 60 * 15) 
    r.hset("sysparms", "beacon_news_num", 300) 
    r.hset("sysparms", "quantity", 1500) 
    r.hset("sysparms", "quantity_duration", 300) 
    r.hset("sysparms", "backend_domain", "svc.zhijixing.com")
    r.hset("sysparms", "domain", "www.9cloudx.com")
    r.hset("sysparms", "loglevel", "info")
    
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
    return int(hval) if hval.isdigit() else hval

logger = loginit(getsysparm("LOGLEVEL"))   
def sendemail(content, rcv_email, title=""):
    from django.core.mail import send_mail
    logger.info("================sendemail============================")
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
    if title != "":
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
       logger.info("Successfully sent email")
       return 0
    except SMTPException:
       logger.exception("Error: unable to send email")
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

def getDataByUrl(urlstr, isservice=False):
    start = time.clock()
    udata = loadFromUrl(urlstr) 
    urlstop = time.clock()  
    diff = urlstop - start  
    logger.info("loadFromUrl(%s) has taken %s" % (urlstr, str(diff)))
    docs = []
    if udata.has_key("docs"):
        for doc in udata["docs"]:
            if doc is None:
                continue
#             if doc["validTime"]=="false" or not doc["validTime"]:
#                 continue
#            doc["id"] = getHashid(doc["url"])
            doc["docid"] = getHashid(doc["url"])
            doc["title"] = doc["title"].replace(" ", "")
            doc["tx"] = doc["text"].replace(" ", "")
            doc["text"] = subDocText(doc["text"])
            doc["copyNum"] = str(doc["copyNum"])
            doc["validTime"] = str(doc["validTime"])
            doc["tms"] = str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"]) 
            docs.append(doc)
        udata["docs"] = docs  
        udata["total"] = str(len(udata["docs"]))
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
    r.expire("quantity:" + client_address, getsysparm("QUANTITY_DURATION"))
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
    logger.info("loadFromUrl(%s) has taken %s" % (urlstr, str(diff)))
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
            doc["title"] = doc["title"].replace(" ", "") 
            doc["copyNum"] = str(doc["copyNum"])
            doc["validTime"] = str(doc["validTime"])
            doc["tms"] = str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"]) 
            docs.append(doc)
        udata["docs"] = docs  
        udata["total"] = str(len(udata["docs"]))
        return doc
    else:
        udata["total"] = "0"
        udata["docs"] = []
    return {}

def subDocText(s):
#    us=unicode(s,"utf8")
#    return s
    if s == "":
        return s
    s = s.replace(" ", "")
#    .replace(",", "，".decode("utf8"))
    us = to_unicode_or_bust(s)
    lc = us[-1]
    dot = "。".decode("utf8")
    comma = "，".decode("utf8")
    ellipsis = " ......".decode("utf8")
    if lc == dot or lc == ".":  # 从尾部判断，如果最后一个字符是"。"或者"." 则返回原始文本
        return s
    else:  # 否则开始进行截取
        slst = us.split(dot)
        if len(slst[-1]) < 55:  # 如果最后一段在"。"之后文本长度小于35,则截断之
            rs= dot.join(slst[0:-1] + [""]).encode("utf8")
            return rs if rs!="" else s
        else:  # 如果 最后一段文字数大于35个，则从尾部开始，截断到最近一个标点符合，包括，
            clst = slst[-1].split(comma)
            rs= (dot.join(slst[0:-1] + [""]) + comma.join(clst[0:-1] + [""])).encode("utf8")
            return rs if rs!="" else s
    return s

def getchannelByid(beaconusr, beaconid): 
    return r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl") 
    # if r.exists("bmk:" + beaconusr + ":" + beaconid) else ""
    
def strfilter(istr):
    return istr.replace("&ldquo;", "").replace("&rdquo;", "").replace("&amp;", "&").replace("&#215;", "X")
    
def pushQueue(qtype,qobj):
    """ push Queue by qobj """
#     logger.info("qtype in pushQueue is "+qtype) 
    qobj["tms"] = "%s" % dt.datetime.now()
    qobj["type"] = qtype    
#     r.lpush("queue:" + qtype, json.dumps(qobj,ensure_ascii=False))
    logger.info("qobj is "+ json.dumps(qobj) ) 
    r.lpush("queue:" + qtype, json.dumps(qobj))

def saveFulltextById(ids,url=""):
    udata={}
    
    def procids(ids):# 截断ids,并以每20个id为一组 向后台提交请求
        if ids is None or ids =="": return {}
        idlist = ids.split(";")
        idstr = ""
        retrycnt = 0
        while len(idlist)>0: 
            logger.info("len(ids) left %d"  % len(idlist) )
            for i in range(20):
                if len(idlist)>0 : idstr = idstr + idlist.pop() + ";" 
            urlstr = "http://%s/research/svc?docid=%s" %(getsysparm("BACKEND_DOMAIN"),idstr) 
            idstr=""
            udata = saveFile(urlstr) 
        return udata
    
    def saveFile(urlstr,retrycnt=0):
        logger.info("proc url="+urlstr)
        udata = bench(loadFromUrl,parms=urlstr)
        if udata.has_key("docs"):
            pipedoc = rdoc.pipeline()
            txt=""
            for doc in udata["docs"]:
                if doc is None :
                    continue
                
                doc["_id"]=str(doc["docId"])
                doc["title"] = strfilter(doc["title"])
                if doc.has_key("fulltext"):
                    txt = doc["fulltext"]
    #                 doc.pop("relatedDocs")
                    logger.info("save fulltext in mongodb:"+doc["_id"])
                    tftxs.save(doc) 
                else:
                    pass
                
                docid = str(doc["docId"])
    #             pipedoc.set("ftx:"+docid,json.dumps(txt))
    #             pipedoc.expire("ftx:"+docid,DOC_EXPIRETIME)
                if not r.hexists("doc:"+docid,"docid"):
                    pipedoc.hset("doc:"+docid,"docid",docid)
#                 if not r.hexists("doc:"+docid,"title"):
                pipedoc.hset("doc:"+docid,"title",doc["title"].rstrip() ) 
                if not r.hexists("doc:"+docid,"text"):
                    pipedoc.hset("doc:"+docid,"text",doc["text"].rstrip() )
                if not r.hexists("doc:"+docid,"copyNum"):
                    pipedoc.hset("doc:"+docid,"copyNum",doc["copyNum"] )  
                if not r.hexists("doc:"+docid,"create_time"):
                    pipedoc.hset("doc:"+docid,"create_time",doc["create_time"] )
                
                pipedoc.hset("doc:"+docid,"url",doc["urls"][0].split(",")[1] )
                pipedoc.hset("doc:"+docid,"host","")
                pipedoc.hset("doc:"+docid,"domain",doc["domain"] )
                domain=doc["domain"]
                host = r.hget("navi",domain)
                host = "" if host is None else host
                if not r.exists("bmk:news:"+getHashid(domain)):
                    addBeacon("news", getHashid(domain), domain, beaconname=domain, desc=host, beacontime="", mindoc="", tag="新闻媒体,媒体".decode("utf8"), headlineonly="0")
            pipedoc.execute()
        else:
            logger.warn( "udata is empty...retrycntis %d" % retrycnt)
            if retrycnt >=getsysparm("RETRY_TIMES"):
                logger.warn( "Attembrough: it's failed again..retrycnt is %d" % retrycnt ) 
                pushQueue("fulltext",{"urlstr":urlstr}) 
                return udata
            else:
                udata = saveFile(urlstr,retrycnt = retrycnt +1 )
            
        return udata
    
    if url!="" :
        urlstr = url
        logger.info( "=saveFulltextById==="+urlstr )
        udata = saveFile(urlstr)
    else:
        logger.info( "=saveFulltextById==="+ids )
        udata = procids(ids)
    return udata 
    
def buildBeaconData(beaconusr, beaconid, start=0, end=-1, isapi=False, orderby="tms"):
    key = "bmk:" + beaconusr + ":" + beaconid
    if r.exists(key):
        refreshBeacon(beaconusr, beaconid)
    else:
        return {}
    udata = {}
    docs = [] 
    channels = []
    channelfromtags = []
    if orderby == "tms":
        doc_lst = r.zrevrange(key + ":doc:tms", start, end)  # 主题文档集合
    else:
        doc_lst = r.zrevrange(key + ":doc:tms", 0, 500)  # 主题文档集合
        
    for docid in doc_lst:
        doc = rdoc.hgetall("doc:" + docid) 
        if doc == {}:
            continue  
        if not isapi:
            doc["tx"] = doc["text"].decode("utf8")
        doc["text"] = subDocText(doc["text"]).decode("utf8")
        if doc.has_key("title"): doc["title"] = doc["title"].decode("utf8") + u"\u3000"
#         doc["domain"] = doc["domain"].decode("utf8") + u"\u3000"
        doc["domain"] = doc["domain"].decode("utf8")
        doc["copyNum"] = str(doc["copyNum"])
        if doc.has_key("popularity"):
            doc["popularity"] = str(doc["popularity"])
        else:
            doc["popularity"] = "0"
        doc["tms"] = str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"])
        
        if doc.has_key("label"):
            doc.pop("label")
        if not doc.has_key("utms"):
            doc["utms"] = doc["tms"]
        docs.append(doc) 
    
#     docs = sorted(docs,key=lambda l:(l["popularity"],l["tms"]),reverse = True)
    if orderby != "tms":
        logger.info("buildBeaconData order by %s" % (orderby,))
        docs = sorted(docs, key=lambda l:(l[orderby], l["tms"]), reverse=True)
        docs = docs[start:end]
    udata["docs"] = docs
    channelstr = r.hget(key, "channels")
    if channelstr is not None and  channelstr != "" :
        for cname in  channelstr.split(","):
            if r.hexists("beacon:channel", cname):
                cobj = {}
                cobj["beaconttl"] = cname
                ckey = r.hget("beacon:channel", cname)
                cobj["beaconusr"] = ckey.split(":")[1]
                cobj["beaconid"] = ckey.split(":")[2]
                cobj["beaconname"] = r.hget("bmk:" + ckey.split(":")[1] + ":" + ckey.split(":")[2], "name")
                channels.append(cobj)
                
    if beaconusr + ":" + beaconid in r.hvals("stock:channel"):  # 如果是概念频道
        for bstr in r.zrevrange("bmk:doc:share", 0, -1):
            bkey = "bmk:" + bstr.replace("|-|", ":")
            tags = r.hget(bkey, "tag") 
            tags = "" if tags is None else tags
            if re.search(r.hget(key, "ttl"), tags): 
                cobj = {}
                cobj["beaconttl"] = r.hget(bkey, "ttl")
                cobj["beaconusr"] = r.hget(bkey, "crt_usr")
                cobj["beaconid"] = r.hget(bkey, "id")
                cobj["beaconname"] = r.hget(bkey, "name")
                if cobj in channels:
                    continue
                channelfromtags.append(cobj)   
            
    udata["channels"] = channels
    udata["channelfromtags"] = channelfromtags
    udata["total"] = str(len(udata["docs"])) 
    return udata

def saveDocsByUrl(urlstr,headlineonly="0"):
    logger.info( "===saveDocsByUrl==="+urlstr)
    udata = bench(loadFromUrl,parms=urlstr)
    pipedoc = rdoc.pipeline()
    def saveText(docs):
        ids_lst=[]
        tms=time.time()
        ids=""
        docs.reverse()
        for doc in docs:
            if doc is None: 
                continue 
#             if doc["validTime"]=="false" or not doc["validTime"]:
#                 continue
    #             docid = getHashid(doc["url"]) 
            docid = str(doc["docId"])
            
            if not rdoc.hexists("doc:"+docid,"url"):
                if tms - long(doc["create_time"])/1000 > 86400*60:#如果是一个月以前的新闻
                    logger.debug("jump fulltext doc:%s, sub tms is %d" % (docid,tms - long(doc["create_time"])/1000) )
                else:
                    ids+=docid+";"
                    logger.debug("save fulltext doc:%s, tms is %d" % (docid,tms) )
            else:
                logger.debug("save doc:%s, tms is %d" % (docid,tms) )

            title = doc["title"]
#             title = title.replace("&ldquo;","").replace("&rdquo;","").rstrip()
            title = strfilter(title)
            pipedoc.hset("doc:"+docid,"docid",docid)
            pipedoc.hset("doc:"+docid,"title",title)
    #                 pipedoc.hset("doc:"+docid,"text",subDocText(doc["text"]).replace(" ",""))
            pipedoc.hset("doc:"+docid,"text",doc["text"].rstrip() )
            pipedoc.hset("doc:"+docid,"copyNum",doc["copyNum"] )
            pipedoc.hset("doc:"+docid,"popularity",doc["popularity"] )
            if doc.has_key("eventId") and doc["eventId"] != -1: 
                pipedoc.hset("doc:"+docid,"eventid",doc["eventId"] )
            pipedoc.hset("doc:"+docid,"create_time",doc["create_time"] )
            pipedoc.hset("doc:"+docid,"utms",tms )
            tms = tms +1 
            pipedoc.hset("doc:"+docid,"domain",doc["domain"] ) 
            pipedoc.hset("doc:"+docid,"isheadline",headlineonly) 
                
            pipedoc.expire("doc:"+docid,getsysparm("DOC_EXPIRETIME")*3)
#         print "to be save fulltext_ids is ",ids 
        if len(ids) > 0: saveFulltextById(ids)
        pipedoc.execute()
    ################## saveText is over ##############################

    if udata.has_key("docs"):
        logger.info("save docs and len is :" + str(len(udata["docs"])))
        saveText(udata["docs"])
             
    return udata

def buildHotBoardData(beaconusr, beaconid, start=0, end= -1, isapi=False, orderby="tms",username=""):
    key = "bmk:" + beaconusr + ":" + beaconid
    logger.info("key is " + key)
    if r.exists(key):
        refreshBeacon(beaconusr, beaconid)
    else:
        return {} 
    udata = {}
    docs = [] 
    channels = []
    channelfromtags = []
    if orderby == "tms":
        doc_lst = r.zrevrange(key + ":doc:tms", start, end)  # 主题文档集合
    elif beaconusr =="rd" and orderby == "utms":
        doc_lst = r.zrevrange(key + ":doc:utms", start, end)  # 主题文档集合
    else:
        doc_lst = r.zrevrange(key + ":doc:tms", 0, 300)  # 主题文档集合 
#     print doc_lst
    for docid in doc_lst:
        subdocs = [] 
        doc = rdoc.hgetall("doc:" + docid) 
        if doc == {}:
            logger.warning("doc %s info is not exists!" % docid)
            continue
#         doc.pop("text")
#         doc.pop("copyNum")

        doc["text"] = subDocText(doc["text"]).decode("utf8")
        doc["title"] = doc["title"].decode("utf8") + u"\u3000"
        doc["copyNum"] = str(doc["copyNum"])
        if doc.has_key("popularity"):
            doc["popularity"] = str(doc["popularity"])
        else:
            doc["popularity"] = "0"
            
        if doc.has_key("eventid"):
            doc["eventid"] = str(doc["eventid"])
        else:
            doc["eventid"] = "-1"
            
        doc["docid"] = docid
        doc["tms"] = str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"])
        doc["domain"] = doc["domain"].decode("utf8")
        if not doc.has_key("utms"):
            doc["utms"] = doc["tms"] 
            
        if doc["eventid"] != "-1":
            doc["beaconusr"] = "doc"
            doc["beaconid"]  = doc.pop("eventid")            
            doc["beaconname"] = r.hget("bmk:doc:"+doc["beaconid"], "name").decode("utf8")
            doc["isbeacon"] = "true"
            if username != "":
                beaconstr = "doc|-|"+doc["beaconid"] 
                if r.zscore("usr:"+username+":fllw",beaconstr) is not None:#频道已经被该用户关注
                    doc["beaconisfllw"] = "true"
                else:
                    doc["beaconisfllw"] = "false"
        else:
            doc["isbeacon"] = "false"
            doc.pop("eventid") 
            
        docs.append(doc)

    if orderby == "tms":
        pass
    elif beaconusr =="rd" and orderby == "utms":
        pass
    else:
        logger.info("buildHotBoardData order by %s" % (orderby,))
        docs = sorted(docs, key=lambda l:(l[orderby]), reverse=True)
        docs = docs[start:end]
#     print docs 
    udata["docs"] = docs
    udata["total"] = str(len(udata["docs"]))
#     r.hset(key, "cnt", len(docs))
    return udata

def dataProcForApi(udata):
    if udata is None:
        udata = {}
        udata["success"] = "false"
        udata["message"] = "data is null,maybe communication is error."
        return udata
        
    if udata.has_key("docs"):
        udata["success"] = "success"
        udata["message"] = "get data okay"
    else:
        udata["success"] = "false"
        udata["message"] = "communication is error or data not exists!"
        return udata
        
    udata["total"] = str(udata["total"]) if udata.has_key("total") else "0"
    
    def proc(doc):
        doc["docid"] = str(doc.pop("docId"))
        doc["eventid"] = str(doc.pop("eventId"))
        doc["validTime"] = str(doc["validTime"])
        doc["popularity"] = str(doc["popularity"])
        doc["copyNum"] = str(doc["copyNum"])
        doc["tms"] = str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"])
#         doc["text"] = subDocText(doc["text"]).decode("utf8")
        return doc
    
    udata["docs"] = [ proc(doc) for doc in udata["docs"] ]
    
    return udata
        
def procChannel(datatype, beaconusr, beaconid, beaconname, days="1", usecache="1"):
    udata = {}
    def getdoc(id, url, tmongo):
        logger.info("fetch url:" + url)
        udata = bench(loadFromUrl, parms=url) 
        if udata.has_key("docs"): 
            udata["_id"] = id
            tmongo.save(udata)
            logger.info("save doc into mongdb :" + id)
        else:
            return udata
        
        ########## 保存每个文档的全文 信息 ####################
        ids = [] 
        for doc in udata["docs"]:
#             if rdoc.exists("doc:"+doc["docid"]): continue
            if rdoc.hexists("doc:"+str(doc["docId"]),"url"): continue
            ids.append(str(doc["docId"]))
        if len(ids)>0:
            pushQueue("fulltext",{"urlstr":"","ids":";".join(ids)}) 
        return udata
    
    if datatype == "popularychannel":
        parm = "popularid"
        tmongo = tpopulary
    elif datatype == "relatedchannel":
        parm = "relatedid"
        tmongo = trelate
    elif datatype == "channelnews":
        parm = "channelid"
        tmongo = tchannel
    elif datatype == "channelpick":
        parm = "channelpick"
        tmongo = tchannelpick
    
    if days == "all":
        after = 0 
    else:
        after = time.time() - 86400 * int(days)
        after = after * 1000
    after = int(after)
    before = int(time.time() * 1000)
    
    if beaconname != "":
        beaconid = getHashid(beaconname)
        ttl = urllib2.quote(beaconname.encode("utf8"))
    else:
        key = "bmk:" + beaconusr + ":" + beaconid
        ttl = r.hget(key, "ttl")
        if ttl is not None:  ttl = urllib2.quote(ttl)
        
    url = "http://%s/research/svc?%s=%s&after=%s&before=%s" % (getsysparm("BACKEND_DOMAIN"), parm, ttl, after, before) 
    if usecache == "1":
        udata = tmongo.find_one({"_id":beaconid})
        if udata is None:
            udata = getdoc(beaconid, url, tmongo)
        pushQueue(datatype,{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
    elif usecache == "0":
        udata = getdoc(beaconid, url, tmongo)
    elif usecache == "2":
        udata = tmongo.find_one({"_id":beaconid})
        pushQueue(datatype,{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
    return udata

def beaconUrl(beaconusr, beaconid, daybefore=1):
    """
                        根据频道所属用户及频道id生成从后台取频道的请求地址
    """
    page = 0
#     if os.name =="posix":
#         length=CHANNEL_NEWS_NUM
#     else:
#         length = 20 
    length = getsysparm("CHANNEL_NEWS_NUM")
    key = "bmk:%s:%s" % (beaconusr,beaconid)
    channel = r.hget(key, "ttl")
    channel = "" if channel is None else channel
#     channel = channel.decode("utf8")
    channel = urllib2.quote(channel)
    mindoc = r.hget(key, "mindoc") 
    mindoc = 0 if mindoc is None else mindoc 
    
    popularid = r.hget(key, "headlineonly")
    popularid = "0" if popularid is None else popularid
  
    if beaconusr == "rd":
        channelparm = "channeleventpick"
    elif beaconusr == "stockmarket":
        channelparm = "channelid"
    else:
        channelparm = "channelpick"
        
    today = dt.date.fromtimestamp(time.time())
#     after = time.mktime(today.timetuple())
#     after = after - daybefore*86400
#     after = (after+2*3600) * 1000
#     before = time.time() * 1000
    if daybefore == -1:
        after = 0
    else:
        after = int((time.time() - daybefore * 86400) * 1000) 
    before = int(time.time() * 1000)
    if int(mindoc) <= 0 :
        urlstr = "http://%s/research/svc?%s=%s&after=%d&before=%d" % (getsysparm("BACKEND_DOMAIN"), channelparm, channel, after, before)
    else:
        urlstr = "http://%s/research/svc?%s=%s&after=%d&before=%d&mindoc=%s" % (getsysparm("BACKEND_DOMAIN"), channelparm, channel, after, before, mindoc)
    return urlstr

def refreshBeacon(beaconusr, beaconid,type=""):
#    key = "bmk:"+username+":"+getHashid(beaconid) 
    key = "bmk:" + beaconusr + ":" + beaconid
    dt = timeDiff(r.hget(key, "last_touch"), time.time())
    updt = timeDiff(r.hget(key, "last_update"), time.time())
    dt = dt if dt < updt else updt  
#     removecnt = 0 if r.hget(key, "removecnt") is None else int(r.hget(key, "removecnt"))
    
#     urlstr = beaconUrl(beaconusr, beaconid)
    if type =="newbeaconadd":#newbeaconadd
        pushQueue("channelpick",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"7"})
        pushQueue("channelpick",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
        return
    
    if not r.hexists(key, "last_touch"):  # 如果不存在上次更新时间,视为未更新过
        logger.warn(key + "'s 'last_touch' is not exists,retrivedocs from backend...")
        if r.exists(key): 
#             pushQueue("beacon", beaconusr, "beacon", beaconid, urlstr=urlstr)
            pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"7"})
            pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
        else:  # 如果没有那么巧,后台队列准备刷新该灯塔时,前台已经删除该灯塔
            logger.warn(key + " maybe deleted via front  so we ignore it...")
            
    elif not r.exists("bmk:" + beaconusr + ":" + beaconid + ":doc:tms"):  # 如果频道文章列表不存在,重新刷新数据 
        pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"7"})
        pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
#     elif removecnt > REMOVE_CNT and dt > REMOVE_KEYUPTIME:
#         logger.warn( "data is old,pushQueue(retirveSimilar)..%s,%s,%d" % (beaconusr, beaconid, dt) )
#         r.hset(key, "last_touch", time.time())  # 更新本操作时间  
#         pushQueue("beacon", beaconusr, "beacon", beaconid,urlstr=urlstr)
    elif dt > getsysparm("KEY_UPTIME"):  # 如果上次更新时间过久,则重新刷新数据
        logger.warn("data is old,pushQueue(retirveSimilar)..%s,%s,%d" % (beaconusr, beaconid, dt))
        r.hset(key, "last_touch", time.time())  # 更新本操作时间  
        
        if beaconusr!="rd":
            pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"7"})
        pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
    else:
        logger.warn("Attembrough: oh,refreshBeacon....but i have nothing to do .. bcz time is %d ,uptms=%d" % (dt, getsysparm("KEY_UPTIME")))
        
def addBeacon(beaconusr, beaconid, beaconttl, beaconname="", desc="", beacontime="", mindoc="", tag="", headlineonly="0"):
    key = "bmk:" + beaconusr + ":" + beaconid
    if r.hexists(key,"ttl"):
        logger.info("--Beacon is exists, refreshBeacon: " + beaconttl)
        refreshBeacon(beaconusr, beaconid)
        return
    else:
        logger.info("--addBeacon--" + beaconttl)
        
    beaconname = beaconttl if beaconname == "" else beaconname
    beacontime = getTime(time.time(), formatstr="%Y%m%d%H%M%S") if beacontime == "" else beacontime
    mindoc = "0" if mindoc == "" else mindoc 
    
    r.hset(key, "id", beaconid)
    r.hset(key, "ttl", beaconttl)
    r.hset(key, "name", beaconname)
    r.hset(key, "desc", desc)
    r.hset(key, "crt_usr", beaconusr)
    r.hset(key, "crt_tms", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S"))) 
    r.hset(key, "last_touch", 0) 
    r.hset(key, "last_update", 0) 
    r.hset(key, "cnt", 0) 
    r.hset(key, "mindoc", mindoc) 
    r.hset(key, "tag", tag) 
    r.hset(key, "headlineonly", headlineonly) 
    
    r.zadd("usr:" + beaconusr + ":fllw", time.time(), beaconusr + "|-|" + beaconid)
    r.zadd("bmk:doc:share", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")), beaconusr + "|-|" + beaconid)
    r.zadd("bmk:doc:share:byfllw", time.time(), beaconusr + "|-|" + beaconid)
    r.zadd("bmk:doc:share:bynews", time.time() , beaconusr + "|-|" + beaconid)
    
    refreshBeacon(beaconusr, beaconid,type="newbeaconadd")

