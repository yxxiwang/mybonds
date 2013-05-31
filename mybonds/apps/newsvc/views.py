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


def index(request):     
    return HttpResponse("hello index")
 
@login_required
def channelnews(request): 
    orderby = request.GET.get("orderby", "news")
    channel=request.GET.get("channel", "")
    page=request.GET.get("page", "0")
    length=request.GET.get("length", "20")
    start=request.GET.get("start", "0")
    num=request.GET.get("num", "20")
    username = request.GET.get("u", getUserName(request)) 
    
    if channel !="":
        channel = urllib2.quote(channel.encode("utf8"))
    urlstr = "http://www.gxdx168.com/research/svc?channelid="+channel+"&page=%s&length=%s" %(page,length)
    
    udata=getDataByUrl(urlstr,True)
    
    udata["docs"] = udata["docs"][int(start): int(start) + int(num)] 
#     udata["tags"] = udata["tags"][0: int(tagnum)] 
#     udata["total"] = str(udata["total"]) 
    return HttpResponse(json.dumps(udata), mimetype="application/json")


@login_required
def channels(request):
    return HttpResponse("channels")
 
def newsdetail(request):  
    username = request.GET.get("u", getUserName(request)) 
    docid=request.GET.get("docid", "")
    rtype=request.GET.get("rtype", "string")
#     print request
    udata={}
    doc ={}
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
    
    if rtype =="mongodb":
        logger.info("fetch fulltext from mongodb,docid=" +docid)
        doc = tftxs.find_one({"_id":docid})
        doc["text"] = ""
        doc["relatedDocs"]=""
        ftx = doc["fulltext"]
        if rtype =="string":
            doc["fulltext"] = list2dict([ftx],"txt")
        else:
            doc["fulltext"] = list2dict([ftx],"txt")
        doc["copyNum"] = str(doc["copyNum"])
        doc["tms"]=str(doc["create_time"]) 
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        doc["success"] = "true"
        doc["message"] = "success return data"
#         doc["success"] = "true"
#         doc["message"] = "success return data"
#         print json.dumps(doc)
        return HttpResponse(json.dumps(doc), mimetype="application/json")
        
    
    if rdoc.exists("doc:"+docid) and rdoc.exists("ftx:"+docid):
        doc = rdoc.hgetall("doc:"+docid) 
        if rtype =="string":
            #在每个段落之前插入两个中文全角空格: \u3000
            txstr = rdoc.get("ftx:"+docid).replace(""", \"""",""", \"\\u3000\\u3000""").replace("""[\"""","""[\"\\u3000\\u3000""")
            ftx = "\r\n".join(json.loads(txstr))
            doc["fulltext"] = list2dict([ftx],"txt")
        else:
            txstr = rdoc.get("ftx:"+docid).replace(""", \"""",""", \"\\u3000\\u3000""").replace("""[\"""","""[\"\\u3000\\u3000""")
            doc["fulltext"] = list2dict(json.loads(txstr),"txt")
#         doc["text"] = subDocText(doc["text"])
        doc["text"] = ""
        doc["copyNum"] = str(doc["copyNum"])
        doc["tms"]=str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        doc["success"] = "true"
        doc["message"] = "success return data"
    elif rdoc.exists("doc:"+docid): 
        doc = rdoc.hgetall("doc:"+docid)
        ftx = doc["text"]
        doc["text"] = ""
        if rtype =="string":
            doc["fulltext"] = list2dict([ftx],"txt")
        else:
            doc["fulltext"] = list2dict([ftx],"txt")
        doc["copyNum"] = str(doc["copyNum"])
        doc["tms"]=str(doc["create_time"]) 
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        doc["success"] = "true"
        doc["message"] = "success return data"
    else:
        logger.warn("redis has no key,fetch fulltext from mongodb,docid=" +docid)
        doc = tftxs.find_one({"_id":docid})
        if doc is None:
            logger.warn("mongodb has no key too,docid=" +docid)
            doc["success"] = "false"
            doc["message"] = "have no data found."
            return HttpResponse(json.dumps(doc), mimetype="application/json")
        doc["text"] = ""
        ftx = doc["fulltext"]
        if rtype =="string":
            doc["fulltext"] = list2dict([ftx],"txt")
        else:
            doc["fulltext"] = list2dict([ftx],"txt")
        doc["copyNum"] = str(doc["copyNum"])
        doc["tms"]=str(doc["create_time"]) 
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        doc["success"] = "false"
        doc["message"] = "have no data found."
    return HttpResponse(json.dumps(doc), mimetype="application/json")

@login_required
def removeDocFromChannel(request):
    print "===removeDocFromChannel==="
#     username = request.GET.get("u", getUserName(request))
    username = getUserName(request)
    op = request.GET.get("o", "service") 
    docid = request.GET.get("docid", "") 
    beaconusr = request.GET.get("beaconusr", "") 
    beaconid = request.GET.get("beaconid", "") 
    
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
    pushQueue("removedoc", key, "removedoc",tag=urllib2.quote(channel), similarid =docid)
    
    r.hincrby(key,"removecnt",1)
    
    r.zrem(key+":doc:tms",docid)
    rdoc.delete("ftx:"+docid)
    rdoc.delete("doc:"+docid)
    udata["message"]="success remove docid[%s] in channel" % docid
    udata["success"] = "true"
# #     udata = bench(loadFromUrl,parms=urlstr)
#     if udata=={}: 
#         udata["message"]="somethings error occured docid[%s] in channel" % docid
#         udata["success"] = "false"
#     else:
#         udata["message"]="success remove docid[%s] in channel" % docid
#         udata["success"] = "true"
#         r.zrem(key+":doc:tms",docid)
    
    if op == "page":
        return HttpResponseRedirect('/news/beaconnews/?orderby=tms&beaconid=%s&beaconusr=%s' %(beaconid,beaconusr))
    
    return HttpResponse(json.dumps(udata), mimetype="application/json") 
    
def channelsbygroup(request):
    groupid = request.GET.get("groupid", "") 
    username = request.GET.get("u", getUserName(request))
    udata={} 
    beacons = [] 
    gobj = {}
    if groupid == "":   
        udata["message"]="groupid is null !" 
        udata["success"] = "false"
        return HttpResponse(json.dumps(udata), mimetype="application/json") 
        
    mybeacons = r.zrevrange("usr:" + username+":fllw",0,-1)
    gobj = r.hgetall("group:"+groupid)
    if gobj is None:
        udata["message"]="group is not exsist !" 
        udata["success"] = "false"
        return HttpResponse(json.dumps(udata), mimetype="application/json") 
#     logging.basicConfig(format='%(asctime)s %(message)s',level=logging.WARN)
#     logger.warn("groupid..."+groupid)
#     logger.info("groupid..."+groupid)
    gobj["groupid"]=groupid
#         gname = "" if gname is None else gname
    for bstr in mybeacons:
#             busr,bid = bstr.split("|-|")
        key = "bmk:"+bstr.replace("|-|",":")
        bttl = r.hget(key,"tag")
        bttl = "" if bttl is None else bttl
        if re.search(gobj["name"],bttl):
            bobj = r.hgetall(key)
            bobj["beaconid"]=bobj.pop("id")
            bobj["isfllw"] = "true"
            beacons.append(bobj)
    
    for bstr in listsub(r.zrevrange("bmk:doc:share",0,-1),mybeacons):
        key = "bmk:"+bstr.replace("|-|",":")
        bttl = r.hget(key,"tag")
        bttl = "" if bttl is None else bttl
        if re.search(gobj["name"],bttl):
            bobj = r.hgetall(key)
            bobj["beaconid"]=bobj.pop("id")
            bobj["isfllw"] = "false" 
            beacons.append(bobj)
        
    
    udata["group"] = gobj
    udata["beacons"] = beacons
    udata["total"] = len(beacons)
    udata["message"]="success list beacons ." 
    udata["success"] = "true"
    return HttpResponse(json.dumps(udata), mimetype="application/json") 
        
def grouplist(request):
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
    return HttpResponse(json.dumps(udata), mimetype="application/json") 
    
def countDocs(request):
    username = getUserName(request)
    startdate = request.GET.get("startdate", "197906013") 
    enddate = request.GET.get("enddate", "20571231")
    beaconid = request.GET.get("beaconid", "")
    beaconusr = request.GET.get("beaconusr", "")
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
        

    
    