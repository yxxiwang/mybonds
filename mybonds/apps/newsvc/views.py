#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext 
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound  
from django.contrib.auth.decorators import login_required, permission_required

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

@login_required
def newsdetail(request):  
    username = request.GET.get("u", getUserName(request)) 
    docid=request.GET.get("docid", "") 
    udata={}
    doc ={}
    if docid =="":
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    print rdoc.exists("doc:"+docid)
    print rdoc.exists("ftx:"+docid)
    if rdoc.exists("doc:"+docid) and rdoc.exists("ftx:"+docid):
        doc = rdoc.hgetall("doc:"+docid)
#         ftxdic= json.loads(rdoc.get("ftx:"+docid))
#         print rdoc.get("ftx:"+docid)
        ftx = " \r\n    ".join(json.loads(rdoc.get("ftx:"+docid)))
        doc["fulltext"] = ftx
        doc["text"] = subDocText(doc["text"])
        doc["copyNum"] = str(doc["copyNum"]) 
        doc["tms"]=str(doc["create_time"])
        doc["create_time"] = timeElaspe(doc["create_time"]) 
        doc["success"] = "true"
        doc["message"] = "success return data"
    else:
        urlstr = "http://www.gxdx168.com/research/svc?docid="+docid
        doc=getDocByUrl(urlstr)
#         print udata 
        if doc.has_key("fulltext"):
#             doc = udata["docs"][0] 
            doc["fulltext"] = " \r\n    ".join(doc["fulltext"])
            rdoc.set("ftx:"+docid,json.dumps(doc["fulltext"])) 
            
            doc["success"] = "true"
            doc["message"] = "success return data" 
        else:
            doc["success"] = "false"
            doc["message"] = "can't retrive data" 
    return HttpResponse(json.dumps(doc), mimetype="application/json")

