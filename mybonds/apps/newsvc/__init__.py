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
from mybonds.apps.newspubfunc import *
# 
REDIS_HOST = 'localhost'
REDIS_PORT = 6379 
REDIS_EXPIRETIME = 186400
DOC_EXPIRETIME = 86400*7
KEY_UPTIME = 1800
QUANTITY = 1500
QUANTITY_DURATION = 300
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
rdoc = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)
#  
# def timeElaspe(create_time, real=False):
#     elaspestr = ""
#     create_time = int(create_time)
#     if create_time == 0:
#         return "历史旧闻".decode("utf8")
#     current_time = time.time()
#     if real:  # 如果传入的create_time 是自然生成,
#         elaspe = int(current_time - create_time)
#     else:  # 如果传入的create_time是 取自后台返回的结果
#         elaspe = int(current_time - create_time / 1000)
#     daybefore = int(elaspe / 86400)
#     if daybefore == 0:
#         hourbefore = int(elaspe / 3600)
#         if hourbefore == 0:
#             minbefore = int(elaspe / 60)
#             elaspestr = str(minbefore) + "分钟前"
#         else:
#             elaspestr = str(hourbefore) + "小时前"
#     else:
#         elaspestr = str(daybefore) + "天前"
#     return elaspestr.decode("utf8")
# 
# def getDataByUrl(urlstr,isservice=False):
#     start = time.clock()
#     udata = loadFromUrl(urlstr) 
#     urlstop = time.clock()  
#     diff = urlstop - start  
#     print "loadFromUrl(%s) has taken %s" % (urlstr,str(diff))
#     docs = []
#     if udata.has_key("docs"):
#         for doc in udata["docs"]:
#             if doc is None:
#                 continue
#             if doc["validTime"]=="false" or not doc["validTime"]:
#                 continue
# #            doc["id"] = getHashid(doc["url"])
#             doc["docid"] = getHashid(doc["url"])
#             doc["title"] = doc["title"].replace(" ","")
#             doc["tx"] = doc["text"].replace(" ","")
#             doc["text"] = subDocText(doc["text"])
#             doc["copyNum"] = str(doc["copyNum"])
#             doc["validTime"] = str(doc["validTime"])
#             doc["tms"]=str(doc["create_time"])
#             doc["create_time"] = timeElaspe(doc["create_time"]) 
#             docs.append(doc)
#         udata["docs"] = docs  
#         udata["total"] = str(len(udata["docs"]) )
#     else:
#         udata["total"] = "0"
#         udata["docs"] = []
#     return udata
#     
# def log_typer(request, act, obj):
#     quantity = 0 
#     client_address = request.META['REMOTE_ADDR']
# #    print "client_address===:" + client_address
#     quantity = r.incr("quantity:" + client_address, 1)
#     if quantity > QUANTITY:
#         return quantity
#     r.expire("quantity:" + client_address, QUANTITY_DURATION)
#     username = getUserName(request)
#     logobj = {}
#     logobj["usr"] = username
#     logobj["ip"] = client_address
#     logobj["act"] = act
#     logobj["o"] = obj
#     logobj["url"] = request.get_full_path()
#     logobj["tms"]=time.time()
#     r.zadd("log", time.time(), json.dumps(logobj))
#     r.hset("usrlst", username, json.dumps(logobj))
#     return quantity
#     
# def getDocByUrl(urlstr):
#     start = time.clock()
#     udata = loadFromUrl(urlstr) 
#     urlstop = time.clock()  
#     diff = urlstop - start  
#     print "loadFromUrl(%s) has taken %s" % (urlstr,str(diff))
#     docs = []
#     if udata.has_key("docs"):
#         for doc in udata["docs"]:
#             if doc is None:
#                 continue
# #             if doc["validTime"]=="false" or not doc["validTime"]:
# #                 continue 
#             doc.pop("urls")
#             doc.pop("relatedDocs")
#             doc["docid"] = getHashid(doc["url"])
#             doc["title"] = doc["title"].replace(" ","") 
#             doc["copyNum"] = str(doc["copyNum"])
#             doc["validTime"] = str(doc["validTime"])
#             doc["tms"]=str(doc["create_time"])
#             doc["create_time"] = timeElaspe(doc["create_time"]) 
#             docs.append(doc)
#         udata["docs"] = docs  
#         udata["total"] = str(len(udata["docs"]) )
#     else:
#         udata["total"] = "0"
#         udata["docs"] = []
#     return doc
# 
# def subDocText(s):
# #    us=unicode(s,"utf8")
# #    return s
#     if s =="":
#         return s
#     s = s.replace(" ", "")
# #    .replace(",", "，".decode("utf8"))
#     us=to_unicode_or_bust(s)
#     lc=us[-1]
#     dot="。".decode("utf8")
#     comma = "，".decode("utf8")
#     ellipsis=" ......".decode("utf8")
#     if lc == dot or lc ==".": #从尾部判断，如果最后一个字符是"。"或者"." 则返回原始文本
#         return s
#     else:#否则开始进行截取
#         slst=us.split(dot)
#         if len(slst[-1]) <35:#如果最后一段在"。"之后文本长度小于35,则截断之
#             return dot.join(slst[0:-1]+[""]).encode("utf8")
#         else:#如果 最后一段文字数大于35个，则从尾部开始，截断到最近一个标点符合，包括，
#             clst=slst[-1].split(comma)
#             return (dot.join(slst[0:-1]+[""])+comma.join(clst[0:-1]+[""] ) ).encode("utf8")
#     return s
        