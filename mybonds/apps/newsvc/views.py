#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required, permission_required
from django.template.defaultfilters import length
from django.utils.encoding import smart_str
import json,re
import csv, string
import sys, time
import redis
from mybonds.apps.newspubfunc import *
from newspubfunc import *
from mybonds.apps.newsvc import *
from mybonds.apps.beacon import Beacon

def index(request):     
    return HttpResponse("hello index")
 
@login_required
def channelnews(request): 
    """获取频道新闻"""
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "doc") 
    beaconname = request.GET.get("beaconname", "") 
    usecache = request.GET.get("usecache", "1")
    api = request.GET.get("api", "")
    days = request.GET.get("days", "1")
    ascii = request.GET.get("ascii", "1")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name")  if beaconname =="" else beaconname
    quantity = log_typer(request, "channelnews", obj)
    udata = {}
    udata["api"]=api 
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
#     if obj is None:
#         udata["success"] = "false"
#         udata["message"] = "it's not exists!" 
#         return HttpResponse(json.dumps(udata), mimetype="application/json")

    udata = procChannel("channelnews",beaconusr,beaconid,beaconname,days,usecache) 
    udata = dataProcForApi(udata)
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def channeleventpick(request): 
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "doc") 
    beaconname = request.GET.get("beaconname", "") 
    api = request.GET.get("api", "")
    days = request.GET.get("days", "1")
    ascii = request.GET.get("ascii", "1")
    usecache = request.GET.get("usecache", "1")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name")  if beaconname =="" else beaconname
    quantity = log_typer(request, "channelpick", obj)
    udata = {}
    udata["api"]=api 
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "50") 
    orderby = request.GET.get("orderby", "utms")
    username = getUserName(request)
    
    try:
        bea = Beacon(beaconusr,beaconid)
        bea.setUsecache(usecache)
        bea.setUsername(username)
        udata = bea.getEventPicklist()
        r.hset("usr:" + username + ":channeltms", beaconusr + ":" + beaconid, time.time())
    except:
        traceback.print_exc()
        udata["success"] = "false"
        udata["message"] = "no data" 
    else:
        udata["success"] = "true"
        udata["message"] = "success retrive data"
#     print udata
#     udata = dataProcForApi(udata)
    udata["api"]=api 
#     udata = procChannel("channelnews",beaconusr,beaconid,beaconname,days,usecache) 
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
    
@login_required
def channelpick(request): 
    """获取频道精选新闻"""
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "doc") 
    beaconname = request.GET.get("beaconname", "") 
    usecache = request.GET.get("usecache", "1")
    api = request.GET.get("api", "")
    days = request.GET.get("days", "1")
    ascii = request.GET.get("ascii", "1")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name")  if beaconname =="" else beaconname
    quantity = log_typer(request, "channelpick", obj)
    udata = {}
    udata["api"]=api 
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
#     if obj is None:
#         udata["success"] = "false"
#         udata["message"] = "it's not exists!" 
#         return HttpResponse(json.dumps(udata), mimetype="application/json")
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5") 
    orderby = request.GET.get("orderby", "tms")
    username = getUserName(request)
#     print beaconusr, beaconid
    try:
        if beaconusr == "rd":
            udata = procChannel("channelpick",beaconusr,beaconid,beaconname,days,usecache)
            udata = dataProcForApi(udata)
        else:
            udata = buildBeaconData(beaconusr, beaconid, start=int(start), end=int(num), isapi=True,orderby=orderby) 
        r.hset("usr:" + username + ":channeltms", beaconusr + ":" + beaconid, time.time())
    except:
        traceback.print_exc()
        udata["success"] = "false"
        udata["message"] = "no data" 
    else:
        udata["success"] = "true"
        udata["message"] = "success retrive data"
#     print udata
#     udata = dataProcForApi(udata)
    udata["api"]=api 
#     udata = procChannel("channelnews",beaconusr,beaconid,beaconname,days,usecache) 
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def popularychannel(request):
    """获取频道自动聚类子频道"""
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "doc") 
    beaconname = request.GET.get("beaconname", "") 
    usecache = request.GET.get("usecache", "1")
    days = request.GET.get("days", "1")
    ascii = request.GET.get("ascii", "1")
    api = request.GET.get("api", "")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name")  if beaconname =="" else beaconname
    quantity = log_typer(request, "popularchannel", obj)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json") 
    
    udata = procChannel("popularychannel",beaconusr,beaconid,beaconname,days,usecache)
    udata = dataProcForApi(udata)
    
    def proc(doc):
        doc["beaconid"]=doc["docid"]
        doc["beaconusr"]="doc"
        doc["beaconname"]=doc["title"]
        doc["beacontime"]=getBeaconTime("doc",doc["beaconid"])
  
#         doc["domain"] = doc["domain"].decode("utf8")
        if not doc.has_key("utms"):
            doc["utms"] = doc["tms"]  
        doc["copyNum"] = str(doc["copyNum"]) 
#         if doc.has_key("domain") : doc.pop("domain")
        if doc.has_key("eventid") : doc.pop("eventid")
#         if doc.has_key("copyNum") : doc.pop("copyNum")
#         if doc.has_key("dateStr") : doc.pop("dateStr") 
#         if doc.has_key("create_time") : doc.pop("create_time")
#         if doc.has_key("popularity") : doc.pop("popularity")
#         if doc.has_key("validTime") : doc.pop("validTime")
#         if doc.has_key("text") : doc.pop("text")
        addBeacon("doc",doc["beaconid"],doc["beaconid"],beaconname=doc["beaconname"],tag="auto",headlineonly="1")
        return doc
        
    if udata.has_key("docs"):
        udata["docs"] =  [ proc(doc) for doc in udata["docs"] ]
        
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def trackdoc(request):
    docid = request.GET.get("docid", "")
    usecache = request.GET.get("usecache", "0")
    days = request.GET.get("days", "all")
    ascii = request.GET.get("ascii", "1")
    api = request.GET.get("api", "")
    quantity = log_typer(request, "trackdoc", docid)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    if docid is None:
        udata["success"] = "false"
        udata["message"] = "it's not exists!" 
        udata["api"]=api
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    def getdoc(docid,url):
        logger.info("fetch url:"+url)
        udata = bench(loadFromUrl,parms=url) 
        if udata.has_key("docs"): 
            udata["_id"]=docid
            ttrack.save(udata)
            logger.info("save doc into mongdb :"+docid) 
        return udata
    if days =="all":
        after = 0 
    else:
        after = time.time() - 86400 * int(days)
        after = after*1000
    after = int(after)
    before = int(time.time() * 1000)
    url = "http://%s/research/svc?trackid=%s&after=%s&before=%s" %(getsysparm("BACKEND_DOMAIN"),docid,after,before) 
    if usecache=="1":
        udata = trelate.find_one({"_id":docid})
        if udata is None:
            udata = getdoc(docid,url)
    else:
        udata = getdoc(docid,url)
        
    udata = dataProcForApi(udata)
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def docextend(request):
    host= request.GET.get("host", "")
    docid= request.GET.get("docid", "")
    usecache = request.GET.get("usecache", "1")
    api = request.GET.get("api", "")
    ascii = request.GET.get("ascii", "1")
    
    quantity = log_typer(request, "docextend", docid)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    if docid is None:
        udata["success"] = "false"
        udata["message"] = "it's not exists!" 
        udata["api"]=api
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    beaconname = rdoc.hget("doc:"+docid,"title")
    beaconname = beaconname if beaconname is not None else ""
    if r.hget("navi:ori",host) is not None: beaconname = "%s-->%s" %(beaconname ,r.hget("navi:ori",host))
    
#     beaconusr= "extend"
    beaconusr= "doc"
    beaconid= docid+getHashid(host)
    beacon = Beacon(beaconusr,beaconid)
    beacon.setUsecache(usecache)
    beacon.add(docid, beaconname=beaconname, desc=host, beacontime="", mindoc="", tag="", headlineonly="0")
    udata = beacon.getExtendlist()
    udata = dataProcForApi(udata)
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def relatedoc(request):
    docid = request.GET.get("docid", "")
    usecache = request.GET.get("usecache", "0")
    days = request.GET.get("days", "all")
    ascii = request.GET.get("ascii", "1")
    
    api = request.GET.get("api", "")
    quantity = log_typer(request, "relatedoc", docid)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    if docid is None:
        udata["success"] = "false"
        udata["message"] = "it's not exists!"
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    def getdoc(docid,url):
        logger.info("fetch url:"+url)
        udata = bench(loadFromUrl,parms=url) 
        if udata.has_key("docs"): 
            udata["_id"]=docid
            trelate.save(udata)
            r.zadd("docrelated",time.time(),docid)
            logger.info("save doc into mongdb :"+docid)
        else:
            udata = {}
            udata["success"] = "false"
            udata["message"] = "communication is error or data not exists!"
        return udata
    
    if days =="all":
        after = 0
    else:
        after = time.time() - 86400 * int(days)
        after = after*1000
    after = int(after)
    before = int(time.time()*1000) 
#     print before
    relatedurl = "http://%s/research/svc?extendid=%s&after=%s&before=%s" %(getsysparm("BACKEND_DOMAIN"),docid,after,before) 
    if usecache=="1":
        udata = trelate.find_one({"_id":docid})
        if udata is None:
            udata = getdoc(docid,relatedurl)
    else:
        udata = getdoc(docid,relatedurl)
    
    udata = dataProcForApi(udata)
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")

@login_required
def relatedchannel(request):
    """获取 热点频道的相关频道"""
    beaconid = request.GET.get("beaconid", "1152493")
    beaconusr = request.GET.get("beaconusr", "doc") 
    beaconname = request.GET.get("beaconname", "") 
    usecache = request.GET.get("usecache", "1")
    days = request.GET.get("days", "all")
    api = request.GET.get("api", "")
    ascii = request.GET.get("ascii", "1")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name") if beaconname =="" else beaconname
    quantity = log_typer(request, "relatedchannel", obj)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
#     if obj is None:
#         udata["success"] = "false"
#         udata["message"] = "it's not exists!" 
#         return HttpResponse(json.dumps(udata), mimetype="application/json")
    udata = procChannel("relatedchannel",beaconusr,beaconid,beaconname,days,usecache) 
    udata = dataProcForApi(udata)
    udata["api"]=api
    username = getUserName(request)
    def proc(doc):
        doc["beaconid"]=doc.pop("docid")
        doc["beaconusr"]="doc"
        doc["beaconname"]=doc.pop("title")
        doc["beacontime"]=getBeaconTime("doc",doc["beaconid"])
        
        if username != "":
            beaconstr = "doc|-|"+doc["beaconid"] 
            if r.zscore("usr:"+username+":fllw",beaconstr) is not None:#频道已经被该用户关注
                doc["isfllw"] = "true"
            else:
                doc["isfllw"] = "false"
                
        if doc.has_key("domain") : doc.pop("domain")
        if doc.has_key("eventid") : doc.pop("eventid")
        if doc.has_key("copyNum") : doc.pop("copyNum")
        if doc.has_key("dateStr") : doc.pop("dateStr") 
#         if doc.has_key("create_time") : doc.pop("create_time")
        if doc.has_key("popularity") : doc.pop("popularity")
        if doc.has_key("validTime") : doc.pop("validTime")
        if doc.has_key("text") : doc.pop("text")
        addBeacon("doc",doc["beaconid"],doc["beaconid"],beaconname=doc["beaconname"],tag="auto",headlineonly="1")
        return doc
        
    if udata.has_key("docs"):
        udata["docs"] =  [ proc(doc) for doc in udata["docs"] ]
        
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
           

@login_required
def hotboard(request):
    """获取 热点频道 面板"""
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "doc")
    beaconname = request.GET.get("beaconname", "")
    usecache = request.GET.get("usecache", "1")
    ascii = request.GET.get("ascii", "1")
    orderby = request.GET.get("orderby", "tms")
    api = request.GET.get("api", "")
    obj = r.hget("bmk:"+beaconusr+":"+beaconid,"name") if beaconname =="" else beaconname
    quantity = log_typer(request, "hotboard", obj)
    udata = {}
    udata["api"]=api
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    if obj is None:
        udata["success"] = "false"
        udata["message"] = "it's not exists!" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
        
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "20") 
    username = getUserName(request)
    
    if beaconname!="":
        beaconid=getHashid(beaconname)
        beaconusr="rd"
#     print beaconusr,beaconid
    try:
#         udata = buildHotBoardData(beaconusr, beaconid, start=int(start), end=int(num), isapi=True,orderby=orderby,username=username)
        udata = newHotBoardData(beaconusr, beaconid,username=username,usecache=usecache)
#         print udata
    except:
        traceback.print_exc()
        udata["success"] = "false"
        udata["message"] = "no data" 
    else: 
        udata["success"] = "true"
        udata["message"] = "success retrive data"
#     return HttpResponse(json.dumps(udata), mimetype="application/json") 
    udata["api"]=api
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
 
@login_required
def newsdetail(request):  
    username = request.GET.get("u", getUserName(request)) 
    docid=request.GET.get("docid", "")
    rtype=request.GET.get("rtype", "string")
    ascii = request.GET.get("ascii", "1")
    api = request.GET.get("api", "")
    udata={}
    doc ={}
    udata["api"]=api
    if docid =="":
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    quantity = log_typer(request, "newsFullText", docid)
    
    def list2dict(lst,key):
        rtlst=[]
        for el in lst:
            di ={}
            di[key]=el
            rtlst.append(di)
        return rtlst
    
    cnt = tftxs.find({"_id":docid}).limit(1).count()
#     if cnt ==0 and rdoc.exists("doc:"+docid):
    if cnt ==0:
        logger.info("fulltext is not exsists, pushQueue: "+docid)
        pushQueue("fulltext",{"urlstr":"","ids":docid}) 

    print "fetch fulltext from mongodb,docid=" +docid
    logger.info("fetch fulltext from mongodb,docid=" +docid)
    doc = tftxs.find_one({"_id":docid})
    if doc is None:
        logger.warn("mongodb has no key ,docid=" +docid)
        doc={}
        doc["success"] = "false"
        doc["message"] = "have no data found."
        doc["api"]=api
        return HttpResponse(json.dumps(doc), mimetype="application/json")
    doc["text"] = ""
#     doc["relatedDocs"]=""
    ftx = doc["fulltext"] 
    txstr = json.dumps(ftx)
    txstr = txstr.replace(""", \"""",""", \"\\u3000\\u3000""").replace("""[\"""","""[\"\\u3000\\u3000""")
    txstr = txstr.replace("""\", ""","""\\u3000\",""").replace("""\"]""","""\\u3000\"]""")
#         print txstr
#         txstr = txstr.replace("&ldquo;","").replace("&rdquo;","")
    ftx = json.loads(txstr)
    doc["fulltext"] = list2dict(ftx,"txt")
    doc["copyNum"] = str(doc["copyNum"])
    doc["tms"]=str(doc["create_time"])
    doc["create_time"] = timeElaspe(doc["create_time"])
    doc["url"] = doc["urls"][0].split(",")[1]
    if doc.has_key("domain") :
        doc["beaconid"] =getHashid(doc["domain"])
        doc["beaconusr"]="news"
        doc["beaconname"]=doc["domain"]
    beacon_lst = []
    if doc.has_key("relatedSites"):  
        for site in doc["relatedSites"]:
            host=site[1]
            domain=site[0]
            total=site[2] if len(site)>2 else "0"
            r.hset("navi:ori",host,domain)
            sobj={}
            sobj["domain"]=domain
            sobj["site"]=host
            sobj["total"]=total
            beacon_lst.append(sobj)
            addBeacon("news", getHashid(domain), domain, beaconname=domain, desc=host, beacontime="", mindoc="", tag="新闻媒体,媒体".decode("utf8"), headlineonly="0")
        doc["relatedsites"] = beacon_lst
    rc_lst=[]
    if doc.has_key("relatedChannel"):
        for rc in doc["relatedChannel"]:
            rcobj={}
            rcobj["beaconusr"]="doc"
            rcobj["beaconid"]=getHashid(rc["channelId"])
            rcobj["beaconname"]= r.hget("bmk:doc:"+rcobj["beaconid"], "name").decode("utf8")
            rc_lst.append(rcobj)
        doc["relatedchannel"] = rc_lst
    ct_lst=[]
    if doc.has_key("category"):
        doc["category"]["beaconusr"]="doc"
        doc["category"]["beaconid"]=getHashid(doc["category"]["channelId"])
        doc["category"]["beaconname"]=r.hget("bmk:doc:"+doc["category"]["beaconid"], "name").decode("utf8")
        if doc["category"].has_key("channelId") : doc["category"].pop("channelId")
        if doc["category"].has_key("channelName") : doc["category"].pop("channelName")
        if doc["category"].has_key("docId") : doc["category"].pop("docId")
        if doc["category"].has_key("docCreateTime") : doc["category"].pop("docCreateTime")
        ct_lst.append(doc["category"])
        doc["category"] = ct_lst
    dc_lst=[]
    if doc.has_key("relatedDocs"):
        for dc in doc["relatedDocs"]:
            dc = rdoc.hgetall("doc:" + str(dc["docId"])) 
            if dc == {}: continue   
            dc["text"] = subDocText(dc["text"]).decode("utf8")
            if dc.has_key("title"): dc["title"] = dc["title"].decode("utf8") + u"\u3000" 
            dc["domain"] = dc["domain"].decode("utf8")
            dc["copyNum"] = str(dc["copyNum"])
            dc["popularity"] = str(dc["popularity"])
            dc["tms"] = str(dc["create_time"])
            dc["create_time"] = timeElaspe(dc["create_time"])
            if dc.has_key("label"): dc.pop("label")
            if not dc.has_key("utms"): dc["utms"] = dc["tms"]
            dc_lst.append(dc)
        doc["relatedDocs"] = dc_lst
            
      
    if doc.has_key("relatedChannel"): doc.pop("relatedChannel") 
#     if doc.has_key("relatedDocs2"): doc.pop("relatedDocs2")
    
    if doc.has_key("relatedSites"): doc.pop("relatedSites")
#     if doc.has_key("relatedDocs"): doc.pop("relatedDocs")
    if doc.has_key("relatedEvent"): doc.pop("relatedEvent")
    if doc.has_key("urls"): doc.pop("urls")
    if doc.has_key("eventId"): doc.pop("eventId")
    if doc.has_key("docId"): doc["docid"] = docid
    
    doc["success"] = "true"
    doc["message"] = "success return data"
#     print json.dumps(doc, ensure_ascii=False)
    doc["api"]=api
    return HttpResponse(json.dumps(doc,ensure_ascii=ascii=="1"), mimetype="application/json")
#     return HttpResponse(json.dumps(doc), mimetype="application/json")

@login_required
def removeDocFromChannel(request):
    print "===removeDocFromChannel==="
#     username = request.GET.get("u", getUserName(request))
    username = getUserName(request)
    op = request.GET.get("o", "service") 
    docid = request.GET.get("docid", "") 
    beaconusr = request.GET.get("beaconusr", "") 
    beaconid = request.GET.get("beaconid", "")
    api = request.GET.get("api", "")
    
#     beaconusr= "ltb"
#     beaconid = "1968416984598300074"
#     docid = "1664429281334879208"
    
    udata={}
    if docid=="" or beaconusr == "" or beaconid == "":
        udata["message"]="docid and channel info must be not null"
        udata["success"] = "false"
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    if username!=beaconusr:
        udata["message"]="only channel user himself have this magic power!"
        udata["success"] = "false"
        return HttpResponse(json.dumps(udata), mimetype="application/json")
     
    
    key = "bmk:" + beaconusr + ":" + beaconid
    channel = r.hget(key,"ttl")
#     channel = to_unicode_or_bust(channel)
    
    if os.name =="nt":
        channel = smart_str(channel)
    
    quantity = log_typer(request, "removeDocFromChannel", "remove "+docid+" from "+to_unicode_or_bust(channel))
#     urlstr="http://www.gxdx168.com/research/svc?u="+urllib2.quote(channel) +"&o=2&likeid=-%s" %(docid)
#     pushQueue("removedoc", key, "removedoc",tag=urllib2.quote(channel), similarid =docid)
    urlstr = "http://%s/research/svc?u=%s&o=2&likeid=-%s" % (getsysparm("BACKEND_DOMAIN"), urllib2.quote(channel), docid)
    pushQueue("removedoc",{"urlstr":urlstr,"channel":channel}) 
#     r.hincrby(key,"removecnt",1) 
    r.zrem(key+":doc:tms",docid)
    rdoc.delete("ftx:"+docid)
    rdoc.delete("doc:"+docid)
    udata["message"]="success remove docid[%s] in channel" % docid
    udata["success"] = "true"    
    if op == "page":
        return HttpResponseRedirect('/news/beaconnews/?orderby=tms&beaconid=%s&beaconusr=%s' %(beaconid,beaconusr))
    udata["api"]=api
    return HttpResponse(json.dumps(udata), mimetype="application/json") 
    
def channelsbygroup(request):
    groupid = request.GET.get("groupid", "") 
    orderby = request.GET.get("orderby", "desc")
    api = request.GET.get("api", "")
    username = request.GET.get("u", getUserName(request))
    ascii = request.GET.get("ascii", "1")
    udata={} 
    beacons = [] 
    gobj = {}
    if groupid == "":   
        udata["message"]="groupid is null !" 
        udata["success"] = "false"
        return HttpResponse(json.dumps(udata), mimetype="application/json") 
        
    gobj = r.hgetall("group:"+groupid)
    if gobj is None or gobj=={}:
        udata["message"]="group is not exsist !" 
        udata["success"] = "false"
        udata["api"]=api
        return HttpResponse(json.dumps(udata), mimetype="application/json") 
    gobj["groupid"]=groupid
    
    if orderby =="desc":
        allbeacons = r.zrevrange("bmk:doc:share",0,-1)
    else:
        allbeacons = r.zrange("bmk:doc:share",0,-1)
        
    mybeacons = r.zrevrange("usr:" + username+":fllw",0,-1)
    for bstr in allbeacons:
        key = "bmk:"+bstr.replace("|-|",":")
        bttl = r.hget(key,"tag")
        bttl = "" if bttl is None else bttl
        if re.search(gobj["name"],bttl):
#             bobj = {}
#             bobj["beaconid"]=r.hget(key,"id")
#             bobj["beaconusr"]=r.hget(key,"crt_usr")
#             bobj["beaconname"]=r.hget(key,"name").decode("utf8")
#             bobj["isfllw"] = "true" if bstr in mybeacons else "false"
            bea = Beacon(r.hget(key,"crt_usr"),r.hget(key,"id"))
            bea.setUsername(username)
            bobj = bea.getLastDoc()
            if bobj=={} : continue
#             print bobj
            beacons.append(bobj)
    
    gobj["name"]=gobj["name"].decode("utf8")
    if gobj.has_key("desc") :gobj["desc"]=gobj["desc"].decode("utf8")
    udata["group"] = gobj
    udata["beacons"] = beacons
    udata["total"] = len(beacons)
    udata["message"]="success list beacons ." 
    udata["success"] = "true"
    udata["api"]=api
#     return HttpResponse(json.dumps(udata), mimetype="application/json") 
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
        
def grouplist(request):
    api = request.GET.get("api", "")
    ascii = request.GET.get("ascii", "1")
    udata={} 
    groups = [] 
    g_lst = r.zrevrange("groups", 0,-1)  # 组集合
    for gid in g_lst:
        group = r.hgetall("group:"+gid)
        group["groupid"]=gid
        groups.append(group)
        
    udata["groups"] = groups
    udata["total"] = len(groups)
    udata["message"]="success list groups ." 
    udata["success"] = "true"
    udata["api"]=api
#     return HttpResponse(json.dumps(udata), mimetype="application/json") 
    return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
    
def channelcounts(request):
    username = getUserName(request)
    startdate = request.GET.get("startdate", "197906013") 
    enddate = request.GET.get("enddate", "20571231")
    lastdays = request.GET.get("lastdays", "7")
    beaconkey = request.GET.get("beaconkey", "")
    withopynum = request.GET.get("copynum", "false")
    
    
    starttms = getUnixTimestamp(startdate) *1000
    endtms =  (getUnixTimestamp(startdate)+86400) * 1000
    doc_cts_key = "channel:"+beaconusr+":"+beaconid+":doc_cts"
#     docstr_lst =r.zrevrangebyscore(doc_cts_key,endtms,starttms)
#     cnt_lst = [ json.load(docstr)["num"] for docstr in docstr_lst ]
#     import numpy as np
#     sumcnt = np.sum(cnt_lst) 
    cnt_lst=[]
    for docstr,tms in r.zrevrangebyscore(doc_cts_key,endtms,starttms,withscores=True):
        cntobj = json.loads(docstr)
        

    
    