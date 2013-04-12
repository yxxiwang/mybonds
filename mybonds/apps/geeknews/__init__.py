#!/usr/bin/python
# -*- coding: utf-8 -*-
from numpy.ma.core import isMA  

import json, numpy, time
import csv, string, random
import sys,os
import redis
import traceback
import urllib2
import datetime as dt 
from mybonds.apps import *
# from django import template
# register = template.Library()
REDIS_HOST = 'localhost'
REDIS_PORT = 6379 
REDIS_EXPIRETIME = 186400
DOC_EXPIRETIME = 86400*7
KEY_UPTIME = 300
QUANTITY = 1500
QUANTITY_DURATION = 300
 
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
rdoc = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)
 
def emailcontent(udata):
    content = """
    <table style="margin:0;padding:0;line-height:1.8" border="0" cellpadding="0" cellspacing="0" width="100%">
        <tbody> """ 
    content_list =[]
    content_list.append(content)
    title_list=[]
    textstr="""
    <tr>
        <td valign="top" width="5%"></td>
        <td width="90%">
          <div style="font-size:13px;border-bottom:2px dotted gray;margin:0px;padding-bottom:12px;">
              <b><a style="color:#0055a2;text-decoration:none" 
                  href="{{url}}" target="_blank">{{title}}</a></b>
            <div>
                 <p><small>{{host}}&nbsp;{{create_time}}&nbsp;</span> 
                 </small></p>
            </div>
            <div>{{text}}</div> 
          </div>
        </td>
        <td valign="top" width="5%"></td>
    </tr>
    """
    beanconstr="""
    <tr >
        <td valign="top" width="5%"></td>
        <td width="90%"> 
        <div style="font-size:13px;border-bottom:2px solid blue;background-color: #f5f5f5;padding:17px 15px 24px 0;">
            {{beaconttl}}
        </div>
        </td>
        <td valign="top" width="5%"></td>
    </tr>
    """
    if not udata.has_key("beacons"):
        return ""
    for beacon in udata["beacons"]:
        if not beacon.has_key("docs"):
            continue 
        if not beacon.has_key("ttl"):
            continue 
        content_list.append(beanconstr.replace("{{beaconttl}}", to_unicode_or_bust(beacon["ttl"])) )
        for doc in beacon["docs"]:
            title = to_unicode_or_bust(doc["title"])
            url = to_unicode_or_bust(doc["url"])
            url = "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
            content= textstr
            content = content.replace("{{url}}", url)
            content = content.replace("{{title}}", title)
            content = content.replace("{{host}}", to_unicode_or_bust(doc["host"]))
            content = content.replace("{{create_time}}", to_unicode_or_bust(doc["create_time"]))
            content = content.replace("{{text}}", to_unicode_or_bust(doc["text"]))
#            "<a href='"+url+"'>"+title+"</a><br><br>"+to_unicode_or_bust(doc["text"])
    #            content+="\r\n\r\n"+ "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
#            title_list.append(title)
            content_list.append(content)
    content_list.append("</tbody></table>")
    return "".join(content_list)
    
def sendEmailFromUserBeacon(username,hour_before=8,otype=""):
#    udata = getAllBeaconDocsByUser(username,hour_before=24)
    if type(hour_before).__name__ != "int":#hour_before maybe unicode,or str
        hour_before = int(hour_before)
#    print type(hour_before).__name__
    beacons = r.smembers("usr:"+username+":fllw")
    beacon_lst=[]
    beaconobj={}
    for beaconstr in beacons:#取所有关注的灯塔的相关主题文档
        beaconusr,beaconid = beaconstr.split("|-|")
        if hour_before < 0:#正常情况刷新灯塔,如果取截至到当前hour_before小时的新闻,则不需刷新灯塔(之前已经刷新过)
            refreshBeacon(beaconusr, beaconid)
        key = "bmk:" + beaconusr + ":" + beaconid
        beaconname = to_unicode_or_bust(r.hget(key,"ttl"))  
        beaconname = "" if beaconname is None  else beaconname
        
        beaconobj=r.hgetall(key)
        
        docs=[]
        doc_lst = r.zrevrange(key+":sml:tms",0,30)    
        for simid in doc_lst:
            docinfo = rdoc.hgetall("doc:" + simid) 
            if len(docinfo.keys()) == 0:
                continue 
            doc = {}
            doc["tms"] = docinfo["tms"]
            elaspe = int(time.time()- int(doc["tms"])/ 1000) 
            if elaspe > hour_before*3600> 0:#取hour_before小时之内的新闻
                continue 
#            print "elaspe:%d,tms:%s" %(elaspe,doc["tms"])
#            print hour_before*10,type(hour_before).__name__
#            doc["create_time"] =  dt.date.fromtimestamp(float(docinfo["tms"])/1000).strftime('%Y-%m-%d') 
            doc["create_time"] =  getTime(float(docinfo["tms"])/1000)+"--"+timeElaspe(float(docinfo["tms"]) )
            doc["host"] = docinfo["host"]
            doc["title"] = docinfo["ttl"]
            doc["tx"] = docinfo["tx"]
            doc["text"]=subDocText(docinfo["tx"])
            doc["url"] = docinfo["url"]
            doc["docid"] = getHashid(docinfo["url"]) 
            docs.append(doc)
            docs = sorted(docs,key=lambda l:(l["tms"]),reverse = True)
        beaconobj["docs"]=docs
        beacon_lst.append(beaconobj)
    udata={}
    udata["beacons"]=beacon_lst
            
    email = r.hget("usr:"+username,"email") 
    tdate = dt.date.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    title ="每日新闻精选".decode("utf8")
    title= "%s (%s)" %(to_unicode_or_bust(title),str(tdate))
    
    content = emailcontent(udata)
    sendemail(content,email,title)
    return 0
#    content_list =[]
#    title_list=[]
#    if not udata.has_key("docs"):
#        pass
#    for doc in udata["docs"]:
#        title = to_unicode_or_bust(doc["title"])
#        url = to_unicode_or_bust(doc["url"])
#        url += "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
#        content= "<a href='"+url+"'>"+title+"</a><br><br>"+to_unicode_or_bust(doc["text"])
##            content+="\r\n\r\n"+ "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
#        title_list.append(title)
#        content_list.append(content)
#    sendemail("<br>".join(title_list)+"<br>"+"<br><br>".join(content_list),usr_email,title)
        
def sendemailbydocid(emails,docids,otype=""): 
    print "================sendemailbydocid============================"
#    docids = docids.replace(",",";")
    urlstr = "http://www.gxdx168.com/research/svc?docid=" + docids.replace(",",";")
    udata=getDataByUrl(urlstr)
#    usr_email = r.hget("usr:"+username,"email")
    for usr_email in emails.split(","):
        content_list =[]
        title_list=[]
        if udata.has_key("docs"):
            for doc in udata["docs"]:
                title = to_unicode_or_bust(doc["title"])
                url = to_unicode_or_bust(doc["url"])
                url += "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
                content= "<a href='"+url+"'>"+title+"</a><br><br>"+to_unicode_or_bust(doc["text"])
    #            content+="\r\n\r\n"+ "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
                title_list.append(title)
                content_list.append(content)
            sendemail("<br><br>".join(content_list),usr_email,title_list[0])
    return 0
            
def sendemail(content, rcv_email,title=""):
    print "================sendemail============================"
    import smtplib, mimetypes
    from smtplib import SMTPException
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.Header import Header
    from email.mime.image import MIMEImage
    sender = 'admin@zhijixing.com'
    if rcv_email == "":
        rcv_email = 'yxxiwang@gmail.com'
    receivers = [rcv_email]

    msg = MIMEMultipart()
    msg['From'] = "zhijixing2012lsw@gmail.com"
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
       smtpObj.quit()
       print "Successfully sent email"
    except SMTPException:
       print "Error: unable to send email"
       traceback.print_exc() 
       
def beacontran(username, beaid, docid):
    udata = {}
    beacon = r.hget("bmk:" + username + ":" + beaid, "ttl")
    ism = r.sismember("bmk:" + username + ":" + beaid + ":doc", docid) 
    ism = ism or r.sismember("bmk:" + username + ":" + beaid + ":doc:related", docid)
    ism = ism or r.sismember("bmk:" + username + ":" + beaid + ":doc:localtag", docid)
    udata["name"] = beacon
    udata["hasdoc"] = ism
#    print "bmk:"+getHashid(beacon_ttl.decode("utf8"))+":doc===="+docid+"=="+beacon_ttl.decode("utf8")
#    print "=beacontran===="
#    print "bmk:" + username + ":" + beaid + ":doc"
#    print docid
    return udata
 
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

def requestUrl(url):
#    import requests
#    r = requests.get(url)
# #    r = requests.get('https://api.github.com', auth=('user', 'pass'))
#    if r.status_code == 200:
#        return 0
#    return r.status_code
    import httplib2 as http
    from urlparse import urlparse
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
    } 
    target = urlparse(url)
    method = 'GET'
    body = ''
    h = http.Http()
    response, content = h.request(target.geturl(), method, body, headers)
    if response.status == 200:
        return 0
    return response.status
    

def getFlagName(type):
    flagname = ""
    if type == "ppl":  # 综览
        flagname = "overview"
    elif type == "pdg":  # 待读
        flagname = "foucs"
    elif type == "rcm":  # 推荐
        flagname = "recomm"
    elif type == "nav":  # 推荐
        flagname = "navi"
    elif type == "rdd":  # 已读
        flagname = "history"
    elif type == "beaconnews":  # 灯塔阅读
        flagname = "beaconnews"
    elif type == "todaynews":  # 今文观止
        flagname = "todaynews"
    return flagname

def getOtype(type):
    suffix = ""
    if type == "ppl":
        suffix = "0"
    elif type == "nav":
        suffix = "2"
    elif type == "rcm":
        suffix = "1"
    elif type == "rdd":
        suffix = "3"
    return suffix
 
# def log_typer(the_func):
#    """
#    Make another a function more beautiful.
#    """
#    def _decorated(*args, **kwargs):
#        print "====log_typer is work here===="
# #        request = args[0]._get_request()
# #        print type(request)
# #        print request
#        return the_func(*args, **kwargs)
#    return _decorated
def logexport():
    import codecs
    import datetime as dt
    logs = r.zrevrange("log", 0, -1, withscores=True)
    infos = ""
    tms = time.time()
    tt = time.gmtime(tms)
    tdate = dt.date.fromtimestamp(tms).strftime('%Y%m%d')
#    ttime = str(tt.tm_hour)+":"+str(tt.tm_min)+":"+str(tt.tm_sec) 
    f = codecs.open("/etc/nginx/static/wangxi/log.csv" + tdate, "w")
    f.write(codecs.BOM_UTF8)
    # f.write( unicodeString.encode( "utf-8" ) )
    for log, tms in logs:
        logobj = json.loads(log)
        ip = logobj["ip"]
        user = logobj["usr"]
        act = logobj["act"]
        obj = logobj["o"]
        url = "http://www.ip.cn/getip.php?action=queryip&ip_url=" + ip + "&from=web"
        # rr= requests.get(url)
        # r.hset("usrlst",logobj["usr"],rr.text)
        if ip == "110.75.186.225":
            r.zrem("log", log)
            continue
        if act == "reserch":
            id = obj
            obj = rdoc.hget("doc:" + id, "url")
            infos = rdoc.hget("doc:" + id, "ttl")
        else:
            infos = ""
        
        if isinstance(obj, unicode):
            print obj
    #        obj = obj.decode("utf8")
    #    r.hset("usrlst",user,ip)
    #    r.hset("ips",ip,ip)
        tt = time.gmtime(tms)
        tdate = dt.date.fromtimestamp(tms).strftime('%Y%m%d')
        ttime = str(tt.tm_hour) + ":" + str(tt.tm_min) + ":" + str(tt.tm_sec)
        logstr = '%s,%s,%s,%s,%s,"%s","%s"' % (tdate, ttime, user, ip, act, obj, infos.decode("utf8"))
        print logstr
    #    f.write(logstr)
        f.write(logstr.encode("utf-8"))
        f.write("\n")
    f.close()

def getGreeting():
    greetobjs = r.zrevrange("greeting", 0, 30, withscores=True)
    greets = []
    for greet, tms in greetobjs:
#        print greet ,tms,timeElaspe(tms),str(time.time())
        greetobj = json.loads(greet)
        greetobj["tms"] = timeElaspe(tms, real=True)
        greets.append(greetobj)
#        if greetobj["act"] == "beacon_save":
#            gstr= "正在建设灯塔:"
#            gstr= "%s %s \n %s -%s" % (greetobj["usr"],gstr.decode("utf8"),greetobj["o"],timeElaspe(tms,real=True) )
#        elif greetobj["act"] == "beacon_save":
#            gstr= "分享了TA的灯塔"
#            gstr= "%s %s \n %s -%s" % (greetobj["usr"],gstr.decode("utf8"),greetobj["o"],timeElaspe(tms,real=True) )
#        elif greetobj["act"] == "apply":
#            gstr= "欢迎新用户:"
#            gstr= " %s \n %s -%s" % (gstr.decode("utf8"),greetobj["usr"],timeElaspe(tms,real=True) )
#        greets.append(gstr) 
    return greets


def greeting_typer(username, act, obj):
    logobj = {}
    logobj["usr"] = username
    logobj["act"] = act
    logobj["o"] = obj
    r.zadd("greeting", time.time(), json.dumps(logobj)) 

    
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
    
    
def refreshTagsUptime(username, otype, num, tagid=None):
    if tagid is None:
        keytms = "usr:%s:%s:taglst" % (username, otype)  # usr:wxi:rcm...
    else:
        keytms = "usr:%s:%s:tag:%s:taglst" % (username, otype, tagid)  # usr:wxi:rcm:tag:10086 ...
    tags = r.lrange(keytms , 0, num)  # 更新tag
    for tag in tags:
        keytms = "usr:%s:%s:tag:%s" % (username, otype, getHashid(tag))
        ct = "0" if r.get(keytms) is None else r.get(keytms)
        dt = timeDiff(ct, time.time())
        if dt > KEY_UPTIME:
            print "tag %s timediff is %d,last uptime is %s" % (tag, dt, ct)
            if otype == "nav":
                pushQueue("navtag", username, otype, tag)
            else:
                pushQueue("tag", username, otype, tag)
            r.set(keytms, time.time())

def checkTagUptime(username, otype, num, tag, tagid):
    rt = 0
    keytms = "usr:%s:%s:tag:%s" % (username, otype, tagid)  # usr:wxi:rcm:tag:10086 ...
    td = timeDiff(r.get(keytms), time.time())
    if not r.exists(keytms): 
        if isinstance(username, unicode): 
            print keytms.encode("utf8") + " is not exists,retrivedocs from backend..."
        else:
            print keytms + " is not exists,retrivedocs from backend..."
        rt = saveTagdoc(username, otype, tag)
    elif td > KEY_UPTIME:
#        if isinstance(username, unicode): 
#            print "data is old,pushQueue(retirveTAG).%s,%s,%d" % (username.encode("utf8"), otype, td)
#        else:
        print "data is old,pushQueue(retirveTAG).%s,%s,%d" % (username, otype, td)
        r.set(keytms, time.time())  # 更新本操作时间
        if rt == 0:
            pushQueue("tag", username, otype, tag)
            refreshTagsUptime(username, otype, num, tagid)
    return rt

def checkUptime(username, otype, num):  
    rt = 0
    try:
        keytms = "usr:%s:%s:uptms" % (username, otype)  # usr:wxi:rcm... 
        dt = timeDiff(r.get(keytms), time.time())
        if not r.exists(keytms):
            print keytms + " is not exists,retrivedocs from backend..." 
            rt = saveDocs(username, otype) 
        elif dt > KEY_UPTIME:
            print "data is old,pushQueue(retirvePPL)..%s,%s,%d" % (username, otype, dt)
            r.set(keytms, time.time())  # 更新本操作时间 
            pushQueue(otype, username, otype)       
        if rt == 0 :   
            refreshTagsUptime(username, otype, num)
    except: 
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                          limit=2, file=sys.stdout) 
    return rt

def pushQueue(qtype, username, otype, tag=None, similarid=None):
#    if isinstance(username, unicode): 
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username, otype)
#    else:
#        print "--pushQueue-[qtype=%s;username=%s;otype=%s;]" % (qtype, username.decode("utf8"), otype)
    qobj = {}
    qobj["usr"] = username
    qobj["o"] = otype
    qobj["tms"] = time.time()
    qobj["type"] = qtype 
    if qtype in ["tag", "navtag"]:
        if isinstance(tag, unicode): 
            urlstr = "http://www.gxdx168.com/research/svc?u=%s&o=%s&tag=%s" % (username, getOtype(otype), tag)
        else:
            urlstr = "http://http://www.gxdx168.com.com/research/svc?u=%s&o=%s&tag=%s" % (username, getOtype(otype), tag.decode("utf8"))
        qobj[qtype] = tag 
    elif qtype == "beacon":
        urlstr = "http://www.gxdx168.com/research/svc?channelid=getchannel(%s)" % (tag)
        qobj[qtype] = tag 
    elif qtype in ["ppl", "rdd", "rcm", "nav"]:
        urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&o=" + getOtype(otype)
    elif qtype == "read":
        urlstr = "http://www.gxdx168.com/research?u=" + username + "&likeid=" + similarid
    elif qtype == "sendemail":
        urlstr = "http://www.gxdx168.com/research?u=" + username + "&docid=" + similarid
        qobj["docid"] = similarid
        qobj[qtype] = tag 

    qobj["url"] = urlstr
    qobj["id"] = getHashid(urlstr)
    r.lpush("queue:" + qtype, json.dumps(qobj))


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
            if doc.has_key("tags") and isservice:
                doc["tagids"]=",".join(doc["tags"][0:2])
                doc["tags"]=doc["tagids"].replace(" ","")
            docs.append(doc)
        udata["docs"] = docs 
    if udata.has_key("tags"):
        udata["tags"] = udata["tags"][0:40]
    return udata


def getAllBeaconDocsByUser(username,start=0,num=100,hour_before=-1,newscnt=10):
    print "=getAllBeaconDocsByUser="+username
#    hour_before=8
    beacons = r.smembers("usr:"+username+":fllw")
    sim_lst=[]
    lst=[]
    for beaconstr in beacons:#取所有关注的灯塔的相关主题文档
        beaconusr,beaconid = beaconstr.split("|-|")
        if hour_before < 0:#正常情况刷新灯塔,如果取截至到当前hour_before小时的新闻,则不需刷新灯塔(之前已经刷新过)
            refreshBeacon(beaconusr, beaconid)
        key = "bmk:" + beaconusr + ":" + beaconid
        beaconname = to_unicode_or_bust(r.hget(key,"ttl"))  
        beaconname = "" if beaconname is None  else beaconname
        lst = r.zrevrange(key+":doc:tms",0,newscnt)
        sim_lst += lst
        for sid in lst:
            rdoc.hset("docid:beacons",sid,beaconusr+"|-|"+beaconid+"|-|"+beaconname)  
 
    udata = {}
    docs = []
    
    sim_lst = list(set(sim_lst))#去除重复新闻
    crt_time=time.time()
    for docid in sim_lst: 
        doc = rdoc.hgetall("doc:" + docid) 
        if len(doc.keys()) == 0:
            continue  
        doc["tms"]=str(doc["create_time"])
        elaspe = int(crt_time- int(doc["tms"])/ 1000)
#        print elaspe
        if hour_before>0 and elaspe > hour_before*3600:#取hour_before小时之内的新闻
            continue
        doc["text"] = subDocText(doc["text"])
        doc["copyNum"] = str(doc["copyNum"]) 
        doc["create_time"] = timeElaspe(doc["create_time"])   
        
        beaconstr = rdoc.hget("docid:beacons",docid)
        beaconusr,beaconid,beaconttl = beaconstr.split("|-|") 
        doc["beaconusr"] = beaconusr
        doc["beaconid"] = beaconid
        doc["beaconttl"] = beaconttl 
        docs.append(doc)
        
#    docs = sorted(docs,key=lambda l:(l["beaconttl"],l["tms"]),reverse = True)
    docs = sorted(docs,key=lambda l:(l["tms"]),reverse = True)
#    docs = docs[int(start): int(start) + int(num)]
    udata["docs"] = docs
    return udata   
    

def refreshDocs(username, beaconid):
    key = "bmk:" + username + ":" + beaconid
    print "=====refreshDocs===="+key
    if not r.exists(key):
        return 
    if r.hexists(key, "last_update"):#
        dt = timeDiff(r.hget(key, "last_update"), time.time())
        if dt < KEY_UPTIME:#如果上次更新时间才过去不久,则不重复更新
            print "attembrough: i have nothing to do .bcz current last_update less than %d second, " % KEY_UPTIME
            return
            
    channel = r.hget(key,"ttl")
    if os.name =="nt":
        channel = channel.decode("utf8")
    page = 0 
    length=50
    urlstr = "http://www.gxdx168.com/research/svc?channelid="+channel+"&page=%s&length=%s" %(page,length)
    udata = saveDocsByUrl(urlstr)
    r.hset(key, "last_update", time.time())  # 更新本操作时间  
    
    if udata.has_key("docs"):
        r.delete(key+":doc:tms")
        for doc in udata["docs"]:
            if doc is None:
                continue
            if doc["validTime"]=="false" or not doc["validTime"]:
                continue
            r.zadd(key+":doc:tms",int(doc["create_time"]),getHashid(doc["url"]))
#         r.expire(key+":doc:tms",DOC_EXPIRETIME)
            
    return 0 
            
def refreshBeacon(username, beaconid):
#    key = "bmk:"+username+":"+getHashid(beaconid) 
    key = "bmk:" + username + ":" + beaconid
    dt = timeDiff(r.hget(key, "last_touch"), time.time())
    if not r.hexists(key, "last_touch"):#如果不存在上次更新时间,视为未更新过
        print key + "'s 'last_touch' is not exists,retrivedocs from backend..." 
        if r.exists(key):
            refreshDocs(username, beaconid)
            r.hset(key, "last_touch", time.time())  # 更新本操作时间  
        else:#如果没有那么巧,后台队列准备刷新该灯塔时,前台已经删除该灯塔
            print key + "is deleted via front  so we ignore it..." 
            
    elif not r.exists("bmk:"+username+":"+beaconid+":doc:tms"):#如果频道文章列表不存在,重新刷新数据
        refreshDocs(username, beaconid)
    elif dt > KEY_UPTIME:#如果上次更新时间过久,则重新刷新数据
        print "data is old,pushQueue(retirveSimilar)..%s,%s,%d" % (username, beaconid, dt)
        r.hset(key, "last_touch", time.time())  # 更新本操作时间  
        pushQueue("beacon", username, "beacon", beaconid)
    else:
        print "Attembrough: oh,refreshBeacon....but i have nothing to do .. bcz time is %d" % dt
        
def buildBeaconData(username, beaconid,start=0,end=-1):
    key = "bmk:" + username + ":" + beaconid
    if r.exists(key):
        refreshBeacon(username, beaconid)
    else:
        return {} 
    udata = {}
    docs = [] 
    doc_lst = r.zrevrange(key + ":doc:tms", start,end)  # 主题文档集合
    for docid in doc_lst:
        doc = rdoc.hgetall("doc:" + docid) 
        if len(doc.keys()) == 0:
            continue 
#         if doc["validTime"]=="false" or not doc["validTime"]:
#             continue 
#         doc["tx"] = doc["text"]
        doc["text"] = subDocText(doc["text"])
        doc["copyNum"] = str(doc["copyNum"])
#         doc["validTime"] = str(doc["validTime"])
        doc["tms"]=str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        docs.append(doc) 
    udata["docs"] = docs  
    udata["total"] = str(len(udata["docs"]) )
#     r.hset(key, "cnt", len(docs))
    return udata
        
def buildJsonData(username, docs, tags=None):
    seeds = []
    for hashid in docs:
        seed = rdoc.hgetall("doc:" + hashid)
        seed["t"] = ""
        seed["hosturl"] = r.hget("navi", seed["host"]) 
        seed["type"] = 4
        seed["tag"] = ""  
        seed["hashid"] = hashid
        seed["username"] = username
        seed["elaspestr"] = seed["crt_tms"]
#        seed["elaspestr"] = timeElaspe(seed["crt_tms"])
        seeds.append(seed)
        
#    print "%s;len(seeds) %d===" % (getHashid(tag_id), len(seeds))  
#        relatestr = seed["related"]
#        for relateid in relatestr.split(','):
#            relateseed = {}
#            relateseed = r.hgetall("relatedocs:" + relateid)
#            relateseeds.append(relateseed)
#        #seed["relatedocs"]=relateseeds 
    data = {}
    data["seeds"] = seeds
    if len(docs) == 0:
        data["have_more"] = 'false'
    else:
        data["have_more"] = 'true'
    data["t"] = int(time.time())
    
    obj = {}
    obj["success"] = 'true'
    obj["message"] = ""
    obj["data"] = data 
    if tags is not None:
        obj["tag"] = tags
    return obj

def getNavTag(url): 
    tag = r.hget("navi:ori", url)
    return tag if tag is not None else url

def getNavUrl(tag):
    urlstr = r.hget("navi", tag) 
    return urlstr if urlstr is not None else tag

def beaconChangeName(username, srcid, dstid): 
    srckey = "bmk:" + username + ":" + srcid
    dstkey = "bmk:" + username + ":" + dstid
    if r.exists(srckey):
        r.rename(srckey, dstkey)
    r.zrem("bmk:doc:share", username + "|-|" + srcid)
    r.zadd("bmk:doc:share", time.time(), username + "|-|" + dstid) 
    r.zrem("bmk:doc:share:byfllw", username + "|-|" + srcid)
    r.zadd("bmk:doc:share:byfllw", time.time(), username + "|-|" + dstid) 
    r.zrem("bmk:doc:share:bynews", username + "|-|" + srcid)
    r.zadd("bmk:doc:share:bynews", time.time(), username + "|-|" + dstid) 
    r.srem("bmk:" + username, srcid)
    r.sadd("bmk:" + username, dstid)
    
    if r.exists(srckey + ":doc"):
        r.rename(srckey + ":doc", dstkey + ":doc")
    if r.exists(srckey + ":doc:related"):
        r.rename(srckey + ":doc:related", dstkey + ":doc:related")
    if r.exists(srckey + ":doc:localtag"):
        r.rename(srckey + ":doc:localtag", dstkey + ":doc:localtag")
    if r.exists(srckey + ":doc:tms"):
        r.rename(srckey + ":doc:tms", dstkey + ":doc:tms")
    if r.exists(srckey + ":sml"):
        r.rename(srckey + ":sml", dstkey + ":sml") 
    if r.exists(srckey + ":sml:tms"):
        r.rename(srckey + ":sml:tms", dstkey + ":sml:tms")
    if r.exists(srckey + ":doc:unchk"):
        r.rename(srckey + ":doc:unchk", dstkey + ":doc:unchk")
    if r.exists(srckey + ":tag:unchk"):
        r.rename(srckey + ":tag:unchk", dstkey + ":tag:unchk")
    if r.exists(srckey + ":fllw"):
        r.rename(srckey + ":fllw", dstkey + ":fllw")

def getTag(displayTag):
    if isinstance(displayTag, unicode): 
        return r.hget("tag:ori", displayTag) 
    else:
        print "displaytag is not unicode,need decode.."
        return r.hget("tag:ori", displayTag.decode("utf8")) 

def saveRelativeDocs(username, relativeid):
    pass

def saveDocsByIDS(docids):
    print "==============geeknews/saveDocsByID============"  
    docstr = ";".join(docids)
    urlstr = "http://www.gxdx168.com/research/svc?docid=" + docstr 
    udata=getDataByUrl(urlstr)
    docs = [] 
    if udata.has_key("docs"):
        docs = udata["docs"]
    hsetDocs(docs)
    
def hsetDocs(docs):
    pipedoc = rdoc.pipeline()
    rtdocs = [] 
    docmap = {} 
    tagstr = ""
    for doc in docs:
        if doc is None:
            continue
        if doc =="null":
            continue
        hashid = getHashid(doc["url"])
        doc["id"] = hashid
        ukey = "doc:" + hashid 
        if doc.has_key("tags"):
            tags = doc["tags"]
#            for tag in tags:
#                r.hset("tag:ori", tag.replace(' ', ''), tag)  
##            tags = [tag.replace(' ', '') for tag in tags] 
            tagstr = "|-|".join(tags)
            
        docmap["ttl"] = doc["title"]
        docmap["host"] = doc["host"]
        docmap["tx"] = doc["text"]
        docmap["url"] = doc["url"]
        docmap["crt_tms"] = doc["create_time"]
        docmap["tms"] = doc["tms"]
        docmap["tags"] = tagstr
        pipedoc.hmset(ukey, docmap)
        pipedoc.hset(ukey, "tags", tagstr)
        rtdocs.append(doc)
    pipedoc.execute() 
    return rtdocs

def saveLocaltagDocs(relatedid,localtag):
    print "==============geeknews/saveLocaltagDocs============"  
    localtag = to_unicode_or_bust(localtag)
    localtag = urllib2.quote(localtag.encode("utf8"))
    urlstr = "http://www.gxdx168.com/research/svc?length=1100&relatedid=" + relatedid+"&localtag="+localtag
    udata=getDataByUrl(urlstr)
    docs = []
    if udata.has_key("docs"):
        docs = udata["docs"]
        docs.reverse()
    return hsetDocs(docs)

def saveRelatedDocs(relatedids):
    print "==============geeknews/saveRelatedDocs============"  
    print type(relatedids)
    if type(relatedids).__name__ == "list":
        relatedstr = ";".join(relatedids)
    else:
        relatedstr = relatedids
    urlstr = "http://www.gxdx168.com/research/svc?length=1100&relatedid=" + relatedstr
    udata=getDataByUrl(urlstr)
    docs = []
    if udata.has_key("docs"):
        docs = udata["docs"]
        docs.reverse()  
    return hsetDocs(docs)   
#return docs
def saveSimilarDocs(similarids):
    print "==============geeknews/saveSimilarDocs============"  
    print type(similarids)
    if type(similarids).__name__ == "list":
        similarstr = ";".join(similarids)
    else:
        similarstr = similarids
    urlstr = "http://www.gxdx168.com/research/svc?length=1100&similarid=" + similarstr
    udata=getDataByUrl(urlstr)
#    start = time.clock() 
#    udata = loadFromUrl(urlstr) 
#    urlstop = time.clock()  
#    diff = urlstop - start  
#    print "loadFromUrl(%s) has taken %s" % (urlstr, str(diff))  
    docs = []
    if udata.has_key("docs"):
        docs = udata["docs"]
        docs.reverse()  
    return hsetDocs(docs)   
            
def saveTagdoc(username, otype, tag, fromdaemon=False):   
    print "==============geeknews/saveTagdoc============" 
    if otype == "nav":
        otag = getNavUrl(tag) 
    else:
        otag = getTag(tag)  # otag has space .
    if otag is None:
        print "error:---cannot get real Tag "
        return 911
    if isinstance(otag, unicode): 
        ltag = otag.replace(' ', '%20')  # ltag trans space to %20
    else:
        print "otag is not unicode,need decode, fromdaemon=" + str(fromdaemon)
        ltag = otag.decode("utf8")
#        ltag = unicode(otag, "utf8")
        ltag = ltag.replace(' ', '%20')  # ltag trans space to %20 
#    print ltag.encode("utf8")
    dlen = 0 
    try:  # &page=1&length=40
        if otype == "nav":
            urlstr = "http://www.gxdx168.com/research/svc?o=%s&tag=%s&page=0&length=90" % (getOtype(otype), ltag)
        else:
            urlstr = "http://www.gxdx168.com/research/svc?u=%s&o=%s&tag=%s&page=0&length=90" % (username, getOtype(otype), ltag)
    #    print urlstr
        rt = 0 
        start = time.clock() 
        udata = loadFromUrl(urlstr) 
        urlstop = time.clock()  
        diff = urlstop - start  
        if fromdaemon:
            print "loadFromUrl(%s) has taken %s" % (urlstr, str(diff))
        else:
            print "loadFromUrl() has taken %s" % (str(diff))
    #    print "udata len is %d" % len(udata) 
        pipe = r.pipeline()
        pipedoc = rdoc.pipeline()
        tagid = getHashid(tag)
        key = "usr:%s:%s:tag:%s" % (username, otype, tagid)  # usr:wxi:rcm:tag:10086 ...

        pipe.zadd("tag:" + otype, time.time(), username + ":" + tag)
        pipe.zincrby("tag:" + otype + ":cnt", username + ":" + tag, 1) 
        pipe.set(key, time.time())
#        pipi.expire(key,REDIS_EXPIRETIME)
        if udata.has_key("tags"):
            tags = udata["tags"] 
            tags.reverse()
            pipe.delete(key + ":taglst")
    #        tags = [tag.replace(' ', '') for tag in tags]
#            print "tags len is %d,[%s]" % (len(tags),tag) 
#            print key + ":taglst"
            for ztag in tags:
                if otype == "nav":  
                    pipe.lpush(key + ":taglst", getNavTag(ztag))
                else:                    
                    if isAscii(ztag):
                        pipe.hset("tag:ori", ztag , ztag)
                        pipe.lpush(key + ":taglst", ztag)
                    else:
                        pipe.hset("tag:ori", ztag.replace(' ', ''), ztag)
                        pipe.lpush(key + ":taglst", ztag.replace(' ', ''))
                    
        #            timescore = time.time()
        #            pipe.zadd(key + ":tag", timescore, tag)
        uid = ""
        relatestr = ""
        docs = []
        relatedocs = []
        docmap = {}
        if udata.has_key("docs"):
            docs = udata["docs"]
            docs.reverse()
            pipe.delete(key + ":lst")
#            pipe.delete(key + ":zset")
            dlen = len(docs)
#        print "docs len is %d" % len(docs) 
        for doc in docs:
            if doc is None: 
                continue
            timescore = int(time.time())
#            print doc["url"]
            hashid = getHashid(doc["url"])  
            ukey = "doc:" + hashid
            if not rdoc.exists(ukey):  # 如果是新贴,将该贴加入总的docs池中,并更新文章时间信息
                docmap["ttl"] = doc["title"]
                docmap["host"] = doc["host"]
                docmap["tx"] = doc["text"]
                docmap["url"] = doc["url"]
                docmap["crt_tms"] = doc["create_time"]
#                docmap["rel_cnt"] = doc["relatedCount"]
#                docmap["sml_cnt"] = doc["similarCount"]
                pipedoc.hmset(ukey, docmap)  
            else:  # 否则,则是旧帖 (或被重复推荐) 
                if rdoc.hget(ukey, "tx") == "":
                    pipedoc.hset(ukey, "tx", doc["text"])
# #            if otype == "ppl":  # 对于综览,按照时间排序(使用sort set)
# #                pipe.zadd(key + ":zset", doc["create_time"], hashid)
#            else:
            pipe.lpush(key + ":lst", hashid)  # 标签&文章关联
        pipe.execute()
        pipedoc.execute() 
    except:
#            traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                          limit=2, file=sys.stdout)
        rt = 2
    savestop = time.clock()  
    diff = savestop - urlstop  
    print "saveTagDocs %s data has taken on %s; and rt is %d" % (dlen, str(diff), rt)  
    return rt

def saveFulltextById(id):
    print "===saveFulltextById==="+id
    if id is None or id =="":
        return
    urlstr = "http://www.gxdx168.com/research/svc?docid="+id
    udata = bench(loadFromUrl,parms=urlstr)
    if udata.has_key("docs"):
        if udata["docs"][0].has_key("fulltext"):
            rdoc.set("ftx:"+id,json.dumps(udata["docs"][0]["fulltext"]))
            rdoc.expire("ftx:"+id,DOC_EXPIRETIME)
#         if udata["docs"].has_key("relatedDocs"):
#             rdoc.set("rltdoc:"+id,json.dumps(udata["docs"]["relatedDocs"])) 


def saveDocsByUrl(urlstr): 
#     start = time.clock() 
#     udata = loadFromUrl(urlstr) 
#     urlstop = time.clock()  
#     diff = urlstop - start
#     print "loadFromUrl(%s) has taken %s" % (urlstr, str(diff)) 
    print "===saveDocsByUrl==="+urlstr
    udata = bench(loadFromUrl,parms=urlstr)  
    try:
        pipe = r.pipeline()
        pipedoc = rdoc.pipeline()  
        if udata.has_key("docs"): 
            for doc in udata["docs"]: 
                if doc is None: 
                    continue
                if doc["validTime"]=="false" or not doc["validTime"]:
                    continue 
                docid = getHashid(doc["url"]) 
                pipedoc.hset("doc:"+docid,"docid",docid)
                pipedoc.hset("doc:"+docid,"title",doc["title"].replace(" ",""))
#                 pipedoc.hset("doc:"+docid,"text",subDocText(doc["text"]).replace(" ",""))
                pipedoc.hset("doc:"+docid,"text",doc["text"].replace(" ",""))
                pipedoc.hset("doc:"+docid,"copyNum",doc["copyNum"] )  
                pipedoc.hset("doc:"+docid,"create_time",doc["create_time"] )    
                pipedoc.hset("doc:"+docid,"url",doc["url"] )       
                pipedoc.hset("doc:"+docid,"host",doc["host"] )  
                pipedoc.hset("doc:"+docid,"domain",doc["domain"] )  
                pipedoc.expire("doc:"+docid,DOC_EXPIRETIME)
                
#                 if not rdoc.exists("ftx:"+docid):
#                     saveFulltextById(docid)
#                 else:
#                     print "attembrough: i have nothing to do ,bcz ftx:"+docid +" is exists.."
#                     print rdoc.get("ftx:"+docid)
        pipedoc.execute()
    except Exception, e:
         traceback.print_exc()
         pipedoc.execute()
         print "error------la---" 
    return udata
 
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
        if len(slst[-1]) <35:#如果最后一段在"。"之后文本长度小于35,则截断之
            return dot.join(slst[0:-1]+[""]).encode("utf8")
        else:#如果 最后一段文字数大于35个，则从尾部开始，截断到最近一个标点符合，包括，
            clst=slst[-1].split(comma)
            return (dot.join(slst[0:-1]+[""])+comma.join(clst[0:-1]+[""] ) ).encode("utf8")
    return s
         