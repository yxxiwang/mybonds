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
    urlstr = "http://www.gxdx168.com/research/svc?docid="+docid
    udata=getDocByUrl(urlstr)
    return HttpResponse(json.dumps(udata), mimetype="application/json")

