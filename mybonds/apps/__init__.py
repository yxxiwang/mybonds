#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time,os
import redis
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA 

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def getUserName(request):
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        username = request.session.get("username")
        if username is None:
            username = "guest" + str(random.randint(100000, 999999))
#            username = "guest"
            request.session.set_expiry(864000)
            request.session["username"] = username
#        userobj.username = username
#        request.session["username"] = username 
    else:
        username = userobj.username
#        request.session["username"] = username 
#    print "username is:"+username
    return username

def to_unicode_or_bust(obj, encoding='utf-8'):
     if obj is None:
         return "" 
     if isinstance(obj, basestring):
         if not isinstance(obj, unicode):
             obj = unicode(obj, encoding)
     return obj
 
def trace_back():
    try:
        return traceback.format_exc()
    except:
        return ''
    
def isAscii(s):
    for c in s:
#        if c not in string.ascii_letters and c not in string.digits:
        if c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_':
            return False
    return True

def bench(func,parms=None): 
    import time
    start = time.clock()   
    rt = func() if parms is None else func(parms)
    stop = time.clock()  
    diff = stop - start  
    print "%s(%s) has taken %s" % (func.func_name,parms, str(diff)) 
    return rt

def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))
 
def getTime(tms):
    if type(tms).__name__ == "str":
        if tms=="":
            tms="0"
        tms=float(tms)
    tt = time.gmtime(tms+3600*8)
    tdate = dt.date.fromtimestamp(tms).strftime('%Y-%m-%d')
    ttime = str(tt.tm_hour)+":"+str(tt.tm_min)+":"+str(tt.tm_sec)
    return "%s %s" %(tdate,ttime)

def subString(s, start=0,end=-1):
    us = unicode(s, 'utf-8')
    gs = us.encode('gb2312')
    n = int(end)
    s = int(start)
    t = gs[s:n]
    while True:
        try:
            unicode(t, 'gbk')
            break
        except:
            n -= 1
            t = gs[s:n]
    return t.decode('gb2312')

def unescape(s):
    """
                类似于js的unescape,将"%u6708cpi"之类的字符串转换为  "月cpi"
              这里用了个不太好的处理办法 当"cpi"这样int(i,16)处理异常时当作ascii字符处理
    """
    tag_id = ""
    for i in s.split('%u'):
        if len(i) > 4: 
                i = i[0:4] + '%u' + i[4:]
                tag_id += unescape(i)
        elif len(i) > 0:
            try:
                tag_id += unichr(int(i, 16))
            except:
                tag_id += i
        else:
            pass
#    print tag_id
    return tag_id

def getHashid(ustr):
    h = 0
    if ustr == None:
        return h
#    ustr=repr(ustr)#如果传入进来的是中文tag(utf8),将其转为str再计算hashid.
    for c in ustr:
        h = numpy.int64(31 * h + ord(c))
    h = abs(h)
    return str(h)

def timeDiff(create_time=None, current_time=None):
    if create_time is None:
        create_time = 0
    create_time = float(create_time)
    if current_time is None:
        current_time = time.time()
#    print "crt_time is %d,cur_time is %d" %(create_time,current_time)
    diff = int(current_time - create_time)
#    diff = int(elaspe / 60)
    return diff
 
def dayDiff(create_time):
    if create_time is None:
        create_time = 0 
    create_time = int(create_time)
    current_time = time.time()
    elaspe = int(current_time - create_time / 1000)
    daybefore = int(elaspe / 86400)
    return daybefore

def loadFromUrl(url):
    import urllib2
    import json
    import httplib2 as http
    try:
        from urlparse import urlparse
    except ImportError:
        from urllib.parse import urlparse
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
    } 
    target = urlparse(url)
    method = 'GET'
    body = ''
    h = http.Http(timeout=30)
    # # If you need authentication some example:
    # if auth:
    #    h.add_credentials(auth.user, auth.password)
    udata = {}
    try:
        response, content = h.request(target.geturl(), method, body, headers)
    except:
#        traceback.print_stack()
        print "Error: (%s) return content is null!!" % (url) 
        traceback.print_exc()
        return {}
    else:
        if content is not None and content!="":
            udata = json.loads(content)
        else:
            print "Error: (%s) return content is null!!" % (url) 
#    except Exception, e:
#         traceback.print_exc()
    return udata
    