#!/usr/bin/python
# -*- coding: utf-8 -*-
from numpy.ma.core import isMA  
import json, numpy, time
import csv, string, random
import sys,os,re
import redis
import traceback
import urllib2
import datetime as dt

from mybonds.apps import *
from mybonds.apps.newspubfunc import *

# from django import template
# register = template.Library()

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
            url = "http://%s/news/research/?likeid=%s&url=%s&title=%s " %(getsysparm("DOMAIN"),getHashid(url),url,title)
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
def sendEmailFindKey(username,email,url):
#     url= "http://"+request.META['HTTP_HOST']+"/apply/setnewpassword?token="+token
#        content=username+""",您好!\r\n欢迎您的注册,在访问过程中有任何疑问及建议可以给我们邮件或者在网站中提交建议,\r\n
#        现在,您可以邀请您的朋友们通过以下链接来指极星注册:\r\n  """.decode("utf8")+url
    content = username
    content+=to_unicode_or_bust("您好,\r\n\r\n<br>已经收到了您的密码重置请求<br>\r\n\r\n请您点击此链接重新设置密码（链接将在 24 小时后失效）: <br><br>\r\n\r\n\r\n\r\n")
    content+=url
    content+=to_unicode_or_bust("\r\n\r\n<br><br><br>这是一封系统邮件，请不要直接回复。")
    return sendemail(content,email,to_unicode_or_bust("指极星:设置新密码"))
    
def sendemailbydocid(email,docid,otype=""): 
    logger.info( "%s==sendemailbydocid====" % getTime(time.time()) )
    if not rdoc.exists("doc:"+docid):
        print type(docid)
        logger.info( "==error:: document is not exsit!!! doc:"+docid)
        return -1
    doc = rdoc.hgetall("doc:"+docid)
    title = to_unicode_or_bust(doc["title"])
    url = to_unicode_or_bust(doc["url"]) 
    
    fulldoc = tftxs.find_one({"_id":docid})
    if fulldoc is not None:
        logger.info("fetch fulltext from mongodb,docid=" +docid)
#         ftx = "&nbsp;<br><br>&nbsp;&nbsp;&nbsp;&nbsp;".join(json.loads(rdoc.get("ftx:"+docid)))
        ftxlist = fulldoc["fulltext"] 
#         print  "<br><br>    ".join(ftxlist)
        spstr = "<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
#         ftx = fulldoc["title"] +spstr + spstr.join(ftxlist)
        ftx = spstr.join(ftxlist)
        ftx = ftx+"<br><br><br><a href='"+doc["url"]+"'>"+"原文地址".decode("utf8")+"</a>"
    else:
        ftx = doc["title"] +"<br><br>    "+doc["text"]
        ftx = ftx+"<br><br>"+ "<a href='"+doc["url"]+"'>"+doc["url"]+"</a><br><br>" 
    content= to_unicode_or_bust(ftx)
#     title_list.append(title)
#     content_list.append(content) 
    content = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=GBK"> 
    </head>
    <body><div class="text"> """+content+"</div></body> </html>"
    return sendemail(content,email,"[分享] ".decode("utf8")+title)
    
#     for usr_email in emails.split(","):
#         content_list =[]
#         title_list=[] 
#         for docid in docids.split(";"):
#             if not rdoc.exists("doc:"+docid):
#                 continue
#             doc = rdoc.hgetall("doc:"+docid)
#             title = to_unicode_or_bust(doc["title"])
#             url = to_unicode_or_bust(doc["url"])
# #             url += "http://www.9cloudx.com/news/research/?likeid=%s&url=%s&title=%s " %(getHashid(url),url,title)
#             if rdoc.exists("ftx:"+docid):
#                 ftx = "&nbsp;<br><br>&nbsp;&nbsp;&nbsp;&nbsp;".join(json.loads(rdoc.get("ftx:"+docid)))
#             else:
#                 ftx = doc["text"] 
# #             content= "<a href='"+url+"'>"+title+"</a><br><br>"+to_unicode_or_bust(ftx)
#             content= to_unicode_or_bust(ftx)
#             title_list.append(title)
#             content_list.append(content) 
#             sendemail("<br><br>".join(content_list),usr_email,title_list[0])
    return 0
            
       
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
     
def getDataByUrl(urlstr,isservice=False):
    start = time.clock()
    udata = loadFromUrl(urlstr) 
    urlstop = time.clock()  
    diff = urlstop - start  
    logger.info( "loadFromUrl(%s) has taken %s" % (urlstr,str(diff)) )
    docs = []
    if udata.has_key("docs"):
        for doc in udata["docs"]:
            if doc is None:
                continue
#             if doc["validTime"]=="false" or not doc["validTime"]:
#                 continue
#            doc["id"] = getHashid(doc["url"])
#             doc["docid"] = getHashid(doc["url"])
            doc["docid"] = str(doc["docId"])
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

def getBeaconNewsCnt(username,beaconusr,beaconid):
    """find channel's news cnt not read since user last read"""
    last_touch_tms = 0
    new_cnt = 0
    last_touch_tms = r.hget("usr:"+username+":channeltms", beaconusr+":"+beaconid)
    last_touch_tms = 0 if last_touch_tms is None else last_touch_tms
    now_tms = time.time()
    
    if os.name =="posix":
        last_touch_tms = float(last_touch_tms)*1000
        now_tms = float(now_tms)*1000
    else:
        last_touch_tms = float(last_touch_tms)
        now_tms = float(now_tms)
#     print last_touch_tms
#     print time.time()
#     print r.zcount("bmk:" + beaconusr + ":" + beaconid +":doc:tms", last_touch_tms, now_tms)
    new_cnt = r.zcount("bmk:" + beaconusr + ":" + beaconid +":doc:tms", last_touch_tms, now_tms)
    return new_cnt
        
def getAllBeaconDocsByUser(username,start=0,num=100,hour_before=-1,newscnt=10):
    logger.info( "=getAllBeaconDocsByUser="+username )
#    hour_before=8
#     beacons = r.smembers("usr:"+username+":fllw")
#     beacons = r.zrevrange("usr:"+username+":fllw",0,-1)
    beacons = r.zrange("usr:"+username+":fllw",0,-1)
    sim_lst=[]
    lst=[]
    udata = {}
    docs = []
#     newcnts = []
    
    for beaconstr in beacons:#取所有关注的灯塔的相关主题文档
        beaconusr,beaconid = beaconstr.split("|-|")
        if hour_before < 0:#正常情况刷新灯塔,如果取截至到当前hour_before小时的新闻,则不需刷新灯塔(之前已经刷新过)
            refreshBeacon(beaconusr, beaconid)
        key = "bmk:" + beaconusr + ":" + beaconid
        
        beaconname = r.hget(key,"ttl")
        beacondisplayname = r.hget(key,"name")
#         if os.name =="nt":
#             beaconname = beaconname.decode("utf8")
#         beaconname = to_unicode_or_bust(r.hget(key,"ttl"))
        
        beaconname = "" if beaconname is None  else beaconname
        lst = r.zrevrange(key+":doc:tms",0,newscnt-1)
#         sim_lst += lst
#         newcnt = getBeaconNewsCnt(username,beaconusr,beaconid)
        for docid in lst:
            doc = rdoc.hgetall("doc:" + docid)
            if len(doc.keys()) == 0:
                continue 
    #         doc["tx"] = doc["text"]
            doc["text"] = subDocText(doc["text"])
            doc["copyNum"] = str(doc["copyNum"]) 
            doc["tms"]=str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"]) 
            doc["beaconusr"] = beaconusr
            doc["beaconid"] = beaconid
            doc["beaconttl"] = beaconname 
            doc["beaconname"] = beacondisplayname 
            doc["newscnt"] = newscnt 
            docs.append(doc) 
#             rdoc.hset("docid:beacons",sid,beaconusr+"|-|"+beaconid+"|-|"+beaconname)
    udata["docs"] = docs
    return udata   
#   
#     sim_lst = list(set(sim_lst))#去除重复新闻
#     crt_time=time.time()
#     for docid in sim_lst: 
#         doc = rdoc.hgetall("doc:" + docid) 
#         if len(doc.keys()) == 0:
#             continue  
#         doc["tms"]=str(doc["create_time"])
#         elaspe = int(crt_time- int(doc["tms"])/ 1000)
# #        print elaspe
#         if hour_before>0 and elaspe > hour_before*3600:#取hour_before小时之内的新闻
#             continue
#         doc["text"] = subDocText(doc["text"])
#         doc["copyNum"] = str(doc["copyNum"]) 
#         doc["create_time"] = timeElaspe(doc["create_time"])   
#         
#         beaconstr = rdoc.hget("docid:beacons",docid)
#         beaconusr,beaconid,beaconttl = beaconstr.split("|-|") 
#         doc["beaconusr"] = beaconusr
#         doc["beaconid"] = beaconid
#         doc["beaconttl"] = beaconttl 
#         docs.append(doc) 
# #    docs = sorted(docs,key=lambda l:(l["beaconttl"],l["tms"]),reverse = True)
# #     docs = sorted(docs,key=lambda l:(l["tms"]),reverse = True)
# #    docs = docs[int(start): int(start) + int(num)]
#     udata["docs"] = docs
#     return udata   
    




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

def beaconChangeName(key, beaconusr, beaconid): 
    srckey = "bmk:" + key
    dstkey = "bmk:" + beaconusr + ":" + beaconid
    if r.exists(srckey):
        r.rename(srckey, dstkey)
    r.zrem("bmk:doc:share", key.replace(":","|-|"))
    r.zadd("bmk:doc:share", time.time(), beaconusr + "|-|" + beaconid)
    r.zrem("bmk:doc:share:byfllw", key.replace(":","|-|"))
    r.zadd("bmk:doc:share:byfllw", time.time(), beaconusr + "|-|" + beaconid)
    r.zrem("bmk:doc:share:bynews", key.replace(":","|-|"))
    r.zadd("bmk:doc:share:bynews", time.time(), beaconusr + "|-|" + beaconid)
    r.zrem("usr:"+key.split(":")[0]+":fllw", key.replace(":","|-|"))
    r.zadd("usr:"+beaconusr+":fllw", time.time(), beaconusr + "|-|" + beaconid)
    
    if r.exists(srckey + ":doc:tms"):
        r.rename(srckey + ":doc:tms", dstkey + ":doc:tms") 
        
    if r.exists("channel:" + key + ":doc_dcnt"):
        r.rename("channel:" + key + ":doc_dcnt", "channel:" + beaconusr + ":" + beaconid + ":doc_dcnt") 
    if r.exists("channel:" + key + ":doc_tcnt"):
        r.rename("channel:" + key + ":doc_tcnt", "channel:" + beaconusr + ":" + beaconid + ":doc_tcnt") 
    
    from mybonds.build import beaconNameHash
    beaconNameHash()

def getTag(displayTag):
    if isinstance(displayTag, unicode): 
        return r.hget("tag:ori", displayTag) 
    else:
        print "displaytag is not unicode,need decode.."
        return r.hget("tag:ori", displayTag.decode("utf8")) 
 

def saveFulltextById(ids,retrycnt=0,url=""):
    logger.info( "===saveFulltextById==="+url )
    udata={}
    if url=="" :
        if ids is None or ids =="":
            return udata
        urlstr = "http://%s/research/svc?docid=%s" %(getsysparm("BACKEND_DOMAIN"),ids)
    else:
        urlstr = url
    if retrycnt >=getsysparm("RETRY_TIMES"):
        logger.warn( "Attembrough: it's failed again..retrycnt is %d" % retrycnt )
#         pushQueue("fulltext", "", "fulltext", "",urlstr=urlstr) 
        pushQueue("fulltext",{"urlstr":urlstr}) 
        return udata
    udata = bench(loadFromUrl,parms=urlstr)
    if udata.has_key("docs"):
        pipedoc = rdoc.pipeline()
        txt=""
        for doc in udata["docs"]:
            if doc is None :
                continue
            if doc.has_key("fulltext"):
                txt = doc["fulltext"]
            else:
                continue
#             elif doc.has_key("text"):
#                 txt = doc["text"]
#                 id = getHashid(doc["url"])

            doc["_id"]=str(doc["docId"])
            doc["title"] = strfilter(doc["title"])
            doc.pop("relatedDocs")
            tftxs.save(doc) 
            
            docid = str(doc["docId"])
#             pipedoc.set("ftx:"+docid,json.dumps(txt))
#             pipedoc.expire("ftx:"+docid,DOC_EXPIRETIME)
            if not r.hexists("doc:"+docid,"docid"):
                pipedoc.hset("doc:"+docid,"docid",docid)
            if not r.hexists("doc:"+docid,"title"):
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
        pipedoc.execute()
    else:
        logger.warn( "udata is empty...retrycntis %d" % retrycnt)
        udata = saveFulltextById(ids,retrycnt+1)
    return udata
#         if udata["docs"].has_key("relatedDocs"):
#             rdoc.set("rltdoc:"+id,json.dumps(udata["docs"]["relatedDocs"])) 

def saveRelatedDocs(relatedurl,relatedid):
    logger.info( "=geeknews/saveRelatedDocs="+relatedurl)  
    udata = bench(loadFromUrl,parms=relatedurl)
    relateids = []
    if not udata.has_key("docs"):
        return relateids
    
    for doc in udata["docs"]:
#         if doc["validTime"]=="false" or not doc["validTime"]:
#             continue
        docid = str(doc["docId"])
        relateids.append(docid)
        beaconname = doc.get("title",docid)
        eventid = str(doc["eventId"]) if doc.has_key("eventId") else "-1"
        if eventid !="-1":
            addBeacon("doc",docid,docid,beaconname=beaconname,tag="auto",headlineonly="1") 

    udata["_id"]=relatedid
    trelate.save(udata)
    logger.info("save info in mongodb,relatedid="+relatedid)
    return relateids

def saveDocsByUrl(urlstr,headlineonly="0",docAsChannel=False):
    logger.info( "===saveDocsByUrl==="+urlstr)
    udata = bench(loadFromUrl,parms=urlstr)
    pipedoc = rdoc.pipeline()
    def saveText(docs):
        ids_lst=[]
        cnt=0
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
                    cnt = cnt+1
                    logger.debug("save fulltext doc:%s, tms is %d" % (docid,tms) )
                if cnt == 20:
                    ids_lst.append(ids)
                    ids=""
                    cnt = 0
            else:
                logger.debug("save doc:%s, tms is %d" % (docid,tms) )

            eventid = str(doc["eventId"]) if doc.has_key("eventId") else "-1"
            if docAsChannel and eventid !="-1" and not r.exists("bmk:doc:"+docid) :
                beaconname = doc.get("title",docid)
                addBeacon("doc",eventid,eventid,beaconname=beaconname,tag="auto",headlineonly=headlineonly)

            title = doc["title"]
#             title = title.replace("&ldquo;","").replace("&rdquo;","").rstrip()
            title = strfilter(title)
            pipedoc.hset("doc:"+docid,"docid",docid)
            pipedoc.hset("doc:"+docid,"title",title)
    #                 pipedoc.hset("doc:"+docid,"text",subDocText(doc["text"]).replace(" ",""))
            pipedoc.hset("doc:"+docid,"text",doc["text"].rstrip() )
            pipedoc.hset("doc:"+docid,"copyNum",doc["copyNum"] )
            pipedoc.hset("doc:"+docid,"popularity",doc["popularity"] )
            if doc.has_key("eventId"): pipedoc.hset("doc:"+docid,"eventid",doc["eventId"] )
            pipedoc.hset("doc:"+docid,"create_time",doc["create_time"] )
            pipedoc.hset("doc:"+docid,"utms",tms )
            tms = tms +1 
            pipedoc.hset("doc:"+docid,"domain",doc["domain"] ) 
            pipedoc.hset("doc:"+docid,"isheadline",headlineonly) 
                
            pipedoc.expire("doc:"+docid,getsysparm("DOC_EXPIRETIME")*3)
        print "ids_lst",ids_lst,ids
        if len(ids_lst) > 0:
            for tids in ids_lst:
                saveFulltextById(tids)
        else:
            saveFulltextById(ids)
        pipedoc.execute()
    ################## saveText is over ##############################

    if udata.has_key("docs"):
        logger.info("save docs and len is :" + str(len(udata["docs"])))
        saveText(udata["docs"])
             
    return udata

def refreshDocs(beaconusr, beaconid,days="1",force=False):
    """更新频道内容,该方法也会被异步调用"""
    key = "bmk:" + beaconusr + ":" + beaconid
    logger.info( "=====refreshDocs===="+key )
    if not r.exists(key):
        logger.warn( "attembrough: i have nothing to do .key:%s is not exists " % key)
        return -1
#     removecnt = 0 if r.hget(key, "removecnt") is None else int(r.hget(key, "removecnt"))
    if r.hexists(key, "last_update") and not force:#
        timediff = timeDiff(r.hget(key, "last_update"), time.time()) 
        if timediff < getsysparm("KEY_UPTIME"):#如果上次更新时间才过去不久,则不重复更新
            logger.warn( "attembrough: i have nothing to do .bcz current last_update diff is %d second, " % timediff )
            return 0 
    daybefore = int(days)
    urlstr = beaconUrl(beaconusr, beaconid,daybefore=daybefore)
    
    if not r.exists(key):
        logger.warn( "attembrough: i have nothing to do .key:%s is not exists ,maybe it be deleted." % key )
        return -1
    
    headlineonly = r.hget(key, "headlineonly")
    headlineonly = "0" if headlineonly is None else headlineonly
    
    if r.hget(key,"crt_usr")=="doc":#说明频道本身原来是新闻,docAsChannel 则为False
        udata = saveDocsByUrl(urlstr,headlineonly=headlineonly,docAsChannel=False)
    else:
        udata = saveDocsByUrl(urlstr,headlineonly=headlineonly,docAsChannel=True)
    
#     if r.hget(key,"crt_usr")!="doc":
#         ttl = r.hget(key,"ttl")
#         ttl = urllib2.quote(ttl)
#         relateurl = "http://%s/research/svc?relatedid=%s" %(getsysparm("BACKEND_DOMAIN"),ttl)
#         relateids = saveRelatedDocs(relateurl,beaconid)
#         logger.info("relateids:")
#         logger.info(relateids)
#         r.hset(key, "channels", ",".join(relateids))
         
    if udata is None or udata=={} :
        return COMMUNICATERROR
    elif udata.has_key("docs"):
        docs = udata["docs"]
    else:
        return SUCCESS
     
#      if len(docs) >0:
    ctskey = "channel:"+beaconusr+":"+beaconid+":doc_cts"
    doc_dcnt_key = ctskey.replace("doc_cts","doc_dcnt")
    doc_tcnt_key = ctskey.replace("doc_cts","doc_tcnt")
    channel_cnt_key = ctskey.replace("doc_cts","cnt") 
# #     r.delete(key+":doc:tms")
#     rmfrom = (int(time.time())-daybefore*86400)*1000
#     rmto = float(r.hget(key, "last_update"))*1000
#     ndel = r.zremrangebyscore(key+":doc:tms",rmfrom,rmto)
#     logger.info("removenews %s  from %d to %d and del %d" %(key+":doc:tms",rmfrom,rmto,ndel) )
#     logger.info("add new data len is %d"  %(len(docs),))
    for doc in docs:
        if doc is None:
            continue
        if beaconusr=="doc":
            r.zadd(key+":doc:tms",int(doc["create_time"]),str(doc["docId"])) 
        else:
            r.zadd(key+":doc:tms:bak",int(doc["create_time"]),str(doc["docId"]))

################ 统计信息   ############################
        docid= str(doc["docId"])
        tms = doc["create_time"]
        if tms is None or tms==0:
            continue
        
        tdate = dt.date.fromtimestamp(float(tms)/1000).strftime('%Y%m%d')
#         r.zadd(key,int(tms),'{"id":%s,"num":%d}' %(docid,doc["copyNum"]))
        tms=getTime(int(tms)/1000)
        tms = re.sub(r":|-|\s", "", tms)
        r.zadd(doc_tcnt_key,long(tms),docid)
        r.hset("copynum",docid,doc["copyNum"])
        r.zadd(doc_dcnt_key,int(tdate),docid)
    ##### end for #####
    if r.exists(key+":doc:tms:bak"):#如果频道数据为空,那么将不会有 key+":doc:tms:bak" 存在,rename的方法会返回错误
        r.rename(key+":doc:tms:bak",key+":doc:tms")
#     today = (dt.date.today() - timedelta(0)).strftime('%Y%m%d')
#     cnt = r.zcount(doc_dcnt_key,int(today),int(today)) 
#     if cnt>0:
#         r.zadd(channel_cnt_key,cnt,int(today))
################ 统计信息  over ############################
            
    r.hset(key, "last_update", time.time())  # 更新本操作时间  
    r.hset(key, "removecnt", 0)  # 更新本操作时间  
    return SUCCESS

        
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
#     if lc == dot or lc ==".": #从尾部判断，如果最后一个字符是"。"或者"." 则返回原始文本
    if lc == dot: #从尾部判断，如果最后一个字符是"。"或者"." 则返回原始文本
        return s
    else:#否则开始进行截取
        slst=us.split(dot)
        if len(slst[-1]) <35:#如果最后一段在"。"之后文本长度小于35,则截断之
            return dot.join(slst[0:-1]+[""]).encode("utf8")
        else:#如果 最后一段文字数大于35个，则从尾部开始，截断到最近一个标点符合，包括，
            clst=slst[-1].split(comma)
            return (dot.join(slst[0:-1]+[""])+comma.join(clst[0:-1]+[""] ) ).encode("utf8")
    return s
         