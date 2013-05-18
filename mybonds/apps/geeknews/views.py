#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound  
import json, urllib2, urllib
import csv, string,re
import sys, time
import redis
import numpy
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required, permission_required
#import mybonds.apps.geeknews.daemonProcess as daemonProcess
from django.template.defaultfilters import length

from mybonds.apps.newspubfunc import *
from mybonds.apps.geeknews import *


def index(request): 
    return HttpResponseRedirect("/news/beaconnews/") 
    # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    otype = request.GET.get("o", "todaynews")
    print "geeknews/index"
#    user = request.GET.get("u", "ltb")
#    password = request.GET.get("password", "1")
#    t = loader.get_template('geek_login.html')  
    # render the login page  
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
#        return HttpResponseRedirect("/news/overview/?o=" + otype) 
        pass
    else:
        flagname = getFlagName(otype)  # return overview,foucs,recomm or history ...
        return HttpResponseRedirect("/news/" + flagname + "/?o=" + otype) 
#    c = Context({ 
# #        "list_tags": tags,
#    })
    flagname = getFlagName(otype)
    return HttpResponseRedirect("/news/" + flagname + "/?o=" + otype) 

@login_required
def init(request,oper): 
    def init_bmk_fllwkeys():
        fllwkeys =r.keys("bmk:*:fllw")
        print fllwkeys
        for fllwkey in fllwkeys:
            bmk,usr,id,fllw = fllwkey.split(":")
            print bmk,usr,id,fllw 
            print r.scard(fllwkey)
            r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),usr+"|-|"+id)
    def init_bmk_newskey():
        keystrs = r.zrevrange("bmk:doc:share",0,-1)
        for keystr in keystrs:
            usr,id = keystr.split("|-|")
            cnt = r.hget("bmk:"+usr+":"+id,"cnt") if r.hget("bmk:"+usr+":"+id,"cnt") is not None else 0
            r.zadd("bmk:doc:share:bynews",cnt,keystr)
    if oper=="init_bmk_fllwkeys":
        init_bmk_fllwkeys()
    elif oper=="init_bmk_newskey":
        init_bmk_newskey()
    return HttpResponse("ok")
    
# @log_typer        
@login_required
def test(request):
    print "---------geeknews/test---------"
    #otype = request.GET.get("o", "all")
#    if otype == "tag" or otype == "all":
#        for i in range(r.llen("queue:tag:error")):
#            qobj = r.rpoplpush("queue:tag:error", "queue:tag")
#    if otype == "ppl" or otype == "all":
#        for i in range(r.llen("queue:ppl:error")):
#            qobj = r.rpoplpush("queue:ppl:error", "queue:ppl")
#    if otype == "rcm" or otype == "all":
#        for i in range(r.llen("queue:rcm:error")):
#            qobj = r.rpoplpush("queue:rcm:error", "queue:rcm")
#    t = loader.get_template('test.html')   
#    a=u'\u5965\u5df4\u9a6c'
#    print a 
#    username = getUserName(request.user) 
#    c = Context({   
#        "otype":otype,
##        "user":request.user,
#        "otypes": ["on", "", "", "", "", ""],
#    })
#    return HttpResponse(t.render(c))
    return HttpResponse("ok")

@login_required
def feedback_reply(request):
    content = request.GET.get("content", "")
    quantity = log_typer(request, "feedback", content)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    userobj = request.user  
    username = getUserName(request) 
    userobj.username = username     
    obj = {}
#    obj["success"]=True
#    obj["message"]="ok"
    obj["usr"] = username
    obj["tx"] = content
    obj["tms"] = time.time()
    if content != "":
        r.lpush("feedback", json.dumps(obj))
    return HttpResponse(json.dumps(obj), mimetype="application/json")

@login_required
def feedbackform(request):
    rtstr = """
        <div class="feedback feedback-single">
        <div class="title">
        <span class="title-l">你的建议可以让我们做得更好</span><!--a href="/rhea" class="title-r">查看全部反馈</a-->
        </div>
        <div id="fbk-reply-box" class="fbk-reply-box">
        <form class="fbk-form">
        <textarea name="content" cols="30" rows="10" placeholder="你的建议..." ></textarea>
        <input type="hidden" name="url" autocomplete="off" placeholder="问题页面链接">
        <input type="hidden" name="email" value="" autocomplete="off" placeholder="电子邮箱（必填）">
        <input type="hidden" name="name" value="" autocomplete="off" placeholder="姓名">
        <input type="hidden" name="mobile" autocomplete="off" placeholder="手机号码">
        <div class="message"></div>
        <label style="height:24px;">
        <input type="submit" name="submit" value="提交"></label>
        <input type="hidden" name="captcha" value="9527">
        </form>
        <div class="success-page">
        <div class="tip-title">提交成功，感谢您的建议.</div>
        <div class="tip-link"><i>3</i>秒后该窗口将自动&nbsp;<a class="btn">关闭</a></div>
        </div>
        </div>
        </div>
        <script type="text/javascript">
        Feedback.fancybox_page();
        </script> 
    """
    return HttpResponse(rtstr)

def research(request):
    # foward request to backend
#    username = request.GET.get("u", "")
    username = request.GET.get("u", getUserName(request))
    likeid = request.GET.get("likeid", "")
    relatedid = request.GET.get("relatedid", "")
    url = request.GET.get("url", "")
    title = request.GET.get("title", likeid) 
    
    quantity = log_typer(request, "reserch", title)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
#    otype = request.GET.get("t", "")
    
    if url != "":
        if likeid != "":
            pushQueue("read", username, "ppl", "", similarid=likeid)
        return HttpResponseRedirect(url)
    else:
        url="http://www.9cloudx.com"

    if likeid != "":
        url = rdoc.hget("doc:" + likeid, "url")
        if url == "" or url is None:
            return HttpResponse('<h1>亲,你想要访问的页面正在建设中..</h1>')
            
        keyid = "usr:" + username + ":rdd"
        r.zadd(keyid + ":tms", time.time(), likeid)  # 更新用户的已读最新文章时间
        r.lpush(keyid + ":lst", likeid)
        r.sadd(keyid, likeid)  # 用户&已读文章关联
#        r.srem("usr:" + username + ":rcm", likeid)# 从推荐列表中移除 
        tags = r.smembers("doc:" + likeid + ":tag")
        for tag in tags:
            r.zadd(keyid + ":tag", int(time.time()), tag)
        
#        url = "http://www.gxdx168.com/research?u=" + username + "&likeid=" + likeid
#        return HttpResponseRedirect(url) 
        pushQueue("read", username, "research", "", similarid=likeid)
#        print url
    return HttpResponseRedirect(url)  

@login_required
def overview(request):
    print "---------geeknews/overview---------"
    quantity = log_typer(request, "ppl", "none")
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>') 
    otype = request.GET.get("o", "0") 
    
#    #转向bootstrap页面
#    return HttpResponseRedirect("/news/todaynews/")
        
    t = loader.get_template('geeknews.html')  
    userobj = request.user
    username = getUserName(request) 
    userobj.username = username    
    request.session["otype"] = otype
    
    rt = checkUptime(username, otype, 50)  # 推送更新标签到队列
    if rt != 0 or getOtype(otype) == "":
        return HttpResponse('<h1>亲,别像猴子一样在浏览器里乱敲地址..</h1>')
    
    tags = r.lrange("usr:" + username + ":" + otype + ":taglst" , 0, 9)
    tags1 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 10, 19)
    tags2 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 20, 29) 
    tags3 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 30, 39) 
    tags4 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 40, 49) 
    c = Context({
        "list_tags": tags,
        "list_tags1": tags1,
        "list_tags2": tags2,
        "list_tags3": tags3,
        "list_tags4": tags4,
        "user": userobj,
        "otype":otype,
#        "greetings":getGreeting(),
        "otypes": ["on", "", "", "", "", ""],
    })
    request.session.set_test_cookie()
#    print request
    return HttpResponse(t.render(c))

@login_required
def history(request):
    print "---------geeknews/history---------"
    quantity = log_typer(request, "rdd", "none") 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    otype = request.GET.get("o", "rdd")
    t = loader.get_template('geeknews.html')  
    userobj = request.user
#    username = getUserName(userobj)
    username = getUserName(request) 
    userobj.username = username    
    request.session["otype"] = otype
    rt = checkUptime(username, otype, 50)  # 推送更新标签到队列
    if rt != 0 or getOtype(otype) == "":
        return HttpResponse('<h1>亲,别像猴子一样在浏览器里乱敲地址..</h1>')
        
    tags = r.lrange("usr:" + username + ":" + otype + ":taglst" , 0, 9)
    tags1 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 10, 19)
    tags2 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 20, 29)
    tags3 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 30, 39) 
    tags4 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 40, 49) 
        
    c = Context({
        "list_tags": tags,
        "list_tags1": tags1,
        "list_tags2": tags2,
        "list_tags3": tags3,
        "list_tags4": tags4,
        "user": userobj,
        "otype":otype,
        "greetings":getGreeting(),
        "otypes": ["", "", "", "", "", "on"],
    })
    return HttpResponse(t.render(c))
    
@login_required
def navi(request, template_name="geeknews.html"):
    print "---------geeknews/foucs---------"
    quantity = log_typer(request, "nav", "none") 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    otype = request.GET.get("o", "nav")
#    t = loader.get_template('geeknews.html')  
    userobj = request.user
#    username = getUserName(userobj)
    username = getUserName(request) 
    userobj.username = username
    request.session["otype"] = otype
    
    tags = [] 
    rt = checkUptime(username, otype, 35)  # 推送更新标签到队列
    if rt != 0 or getOtype(otype) == "":
        return HttpResponse('<h1>亲,别像猴子一样在浏览器里乱敲地址..</h1>') 
    tags = r.lrange("usr:" + username + ":" + otype + ":taglst" , 0, 6)
    tags1 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 7, 13)
    tags2 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 14, 20)
    tags3 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 21, 27) 
    tags4 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 28, 34) 
        
    return render_to_response(template_name, {
        "list_tags": tags,
        "list_tags1": tags1,
        "list_tags2": tags2,
        "list_tags3": tags3,
        "list_tags4": tags4,
        'current_path': '/news/recomm/?o=rcm',
        "user": userobj,
        "otype":otype,
        "greetings":getGreeting(),
        "otypes": ["", "", "", "on", "", ""],
    }, context_instance=RequestContext(request))

@login_required
def recomm(request, template_name="geeknews.html"):
    print "geeknews/recomment" 
    quantity = log_typer(request, "rcm", "none") 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    otype = request.GET.get("o", "rcm") 
    last = request.GET.get("last", "0")
    userobj = request.user
#    username = getUserName(userobj)
    username = getUserName(request) 
    userobj.username = username
    request.session["otype"] = otype
     
    tags = []
    
    rt = checkUptime(username, otype, 50)  # 推送更新标签到队列
    if rt != 0 or getOtype(otype) == "":
        return HttpResponse('<h1>亲,别像猴子一样在浏览器里乱敲地址..</h1>')
    
    tags = r.lrange("usr:" + username + ":" + otype + ":taglst" , 0, 9)
    tags1 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 10, 19)
    tags2 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 20, 29)
    tags3 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 30, 39) 
    tags4 = r.lrange("usr:" + username + ":" + otype + ":taglst" , 40, 49) 
        
    return render_to_response(template_name, {
        "list_tags": tags,
        "list_tags1": tags1,
        "list_tags2": tags2,
        "list_tags3": tags3,
        "list_tags4": tags4,
        'current_path': '/news/recomm/?o=rcm',
        "onday":last,
        "user": userobj,
        "otype":otype,
        "greetings":getGreeting(),
        "otypes": ["", "", "on", "", "", ""],
    }, context_instance=RequestContext(request))
    

@login_required
def tagdoc(request, tag, template_name="geeknews.html"):  # 获得某个标签的关联标签信息
    print "geeknews/tagdoc" 
    quantity = log_typer(request, "tag", tag)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')

#    username = request.session['username']
    otype = request.GET.get("o", "ppl") 
    last = request.GET.get("last", "0")
#    otype = request.session['otype']) 
    userobj = request.user 
    username = getUserName(request) 
    userobj.username = username
    request.session["otype"] = otype
#    tag = request.GET.get("tag", "all")
    if isinstance(tag, unicode): 
        print "is unicode!"
#        print tag.encode("utf8") 
#        ltag = unicodedata.normalize('NFKD', tag).encode('ascii','ignore')
 
#    tag = unicode(tag.strip(codecs.BOM_UTF8), 'utf-8')
#    print "username is %s,otype is %s,tag is %s" % (username, otype, tag)
#    key = "tag:%s:%s" % (otype, tagid)  # usr:wxi:rcm:tag:10086 ... 
#    print "tag's key==" + key
#    if r.zrank(key, username) is None:  # 标签信息缓存中不存在 
    tagid = getHashid(tag)
    rt = checkTagUptime(username, otype, 50, tag, tagid)    
    if rt != 0 or getOtype(otype) == "":
        return HttpResponse('<h1>亲,别像猴子一样在浏览器里乱敲地址..</h1>')
#    print tagid
    keytms = "usr:%s:%s:tag:%s" % (username, otype, tagid)  # usr:wxi:rcm:tag:10086 ...
    r.zadd("tag:" + otype, time.time(), username + ":" + tag)
    r.zincrby("tag:" + otype + ":cnt", username + ":" + tag, 1)
    
#    docs = r.lrange(key, 0 , -1)  # 取出所有数据
#    obj = buildJsonData(username,docs)
    tags = r.lrange(keytms + ":taglst" , 0, 9)  # tag:z:ppl:35218736511:taglst
    tags1 = r.lrange(keytms + ":taglst" , 10, 19)  # tag:z:ppl:35218736511:taglst
    tags2 = r.lrange(keytms + ":taglst" , 20, 29)  # tag:z:ppl:35218736511:taglst
    tags3 = r.lrange(keytms + ":taglst" , 30, 39)  # tag:z:ppl:35218736511:taglst
    tags4 = r.lrange(keytms + ":taglst" , 40, 49)  # tag:z:ppl:35218736511:taglst
#    print "tags len is %d,[%s]" % (len(tags), tag) 
#    print keytms + ":taglst"
    
    if otype == "rcm":
        otypes = ["", "", "on", "", "", ""]
    elif otype == "ppl":
        otypes = ["on", "", "", "", "", ""]
    elif otype == "rdd":
        otypes = ["", "", "", "", "", "on"]
    elif otype == "nav":
        otypes = ["", "", "", "on", "", ""]
    else:
        otypes = ["", "", "", "", "", "on"] 
    return render_to_response(template_name, {
        "list_tags": tags,
        "list_tags1": tags1,
        "list_tags2": tags2,
        "list_tags3": tags3,
        "list_tags4": tags4,
        "ori_tag": tag,
#        'current_path': request.get_full_path(),
        'current_path':'/news/tagdoc/' + tag + '/?o=rcm',
        "onday":last,
        "user": userobj,
        "otype":otype,
        "otypes": otypes,
    }, context_instance=RequestContext(request))
    
#@login_required
#def load_similar(request):
#    username = request.GET.get("u", getUserName(request))
#    start = request.GET.get("start", "0")
#    num = request.GET.get("num", "5")
#    similarid = request.GET.get("similarid", "")
#    if similarid != "":
#        saveSimilarDocs([similarid]) 
#        r.lpush("docsml:" + similarid + ":lst", similarid)
#        docs = r.lrange("docsml:" + similarid + ":lst", 0 , -1)
##        docs = docs[int(start): int(start) + int(num)]  
#        obj = buildJsonData(username, docs)
#        return HttpResponse(json.dumps(obj), mimetype="application/json")

@login_required
def load_seeds(request):
#    user = request.GET.get("u", "ltb")
    # if request.is_ajax(): 
    otype = request.GET.get("t", "")
    quantity = log_typer(request, "load_seeds", otype) 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5")
    last = request.GET.get("last", "0")
    tag_id = request.GET.get("tag_id", "undefined")
    order = request.GET.get("order", "undefined")
    username = request.GET.get("u", getUserName(request))
     
#    r = redis.StrictRedis(host='localhost', port=6380, db=0)
    keyid = "usr:" + username + ":" + otype
    rddkey = "usr:" + username + ":rdd"
    
    if not (tag_id == "undefined" or tag_id == ""):  # 如果按照tag过滤
        if isinstance(tag_id, unicode): 
            print "==tag in load_seeds is unicode!"
#            tag_id = tag_id.replace('%','\\') 
            if not isAscii(tag_id):
#                tag_id = "".join([ (len(i)>0 and unichr(int(i,16)) or "") for i in tag_id.split('%u') ])
                tag_id = unescape(tag_id)
#            print tag_id
#            print repr(tag_id)
#            tag_id=tag_id.encode("utf8") 
#            print tag_id
#            print repr(tag_id).encode("utf8")
#        else:
#            tag_id=tag_id.decode("utf8")
        keyid = "usr:%s:%s:tag:%s" % (username, otype, getHashid(tag_id)) 
#    if otype =="ppl":
#        docs = r.zrevrange(keyid + ":zset", 0 , -1)  # 取出所有列表数据
#    else:
    docs = r.lrange(keyid + ":lst", 0 , -1)  # 取出所有列表数据
#    if not otype == "rdd":  # 过滤掉阅读历史的数据
#        docs = [doc for doc in docs if not r.sismember(rddkey, doc)]  
#    if last != "0":  # 过滤出1天或者7天内的数据
#        docs = [doc for doc in docs if dayDiff(rdoc.hget("doc:" + doc, "crt_tms")) <= int(last) ]  
 
    if isinstance(username, unicode): 
        print "load_seed,keyid is: %s;docs len is :%d" % (keyid.encode("utf8"), len(docs))
    else:
        print "load_seed,keyid is: %s;docs len is :%d" % (keyid, len(docs))
        
    docs = docs[int(start): int(start) + int(num)] 
    
    if order == "withtag":  # 如果附带标签数据
        checkUptime(username, otype, 10)  # 推送更新标签到队列
        tags = r.lrange("usr:" + username + ":" + otype + ":taglst" , 0, 9)
        obj = buildJsonData(username, docs, tags)
    else:
        obj = buildJsonData(username, docs)
    # uobj = urllib2.urlopen('http://www.geekpark.net/ajax/load_seeds/?order=undefined&start=0&num=24&tt=1352271348055&t=')
    # encoded = json.dumps(head_list)
    # uobj.close()
#    print request 
    # udata = loadFromUrl('http://www.geekpark.net/ajax/load_seeds/?order=undefined&start=0&num=24&tt=1352271348055&t=')
    response = HttpResponse(json.dumps(obj), mimetype="application/json")
#    response = HttpResponse(json.dumps(obj))
    return response
     
@login_required
def retriveData(request):
    print "geeknews/retriveData..."
#    print request
    otype = request.GET.get("o", "")
    if otype == "":
        return "otype is None!"  
#    username = getUserName(request.user)    
    username = getUserName(request)  
    rt = saveDocs(username, otype) 
    if rt == 0:
        print "save data is ok"
    else:
        print "error----"
    return HttpResponseRedirect("/news/?o=" + otype) 
#  
# def get_cast_list(request, poll_id):
#    # return HttpResponse("You're looking at poll %s." % poll_id)
#    head_list = [('Duration', 'CURRENT YLD', 'PREV YLD', 'CHANGE', '1 WK YLD', '1 MO YLD', '6 MO YLD'),
#                 ('1-Month', '1.12', '0.22', '1.1', '1.1', '2.2', '2.1'),
#                ];
#    # writer = csv.writer(sys.stdout)
#    writer = csv.writer(open("testcsv.data", 'w'))
#    for item in head_list:
#      writer.writerow(item)
#
#    response = HttpResponse()
#    # response = HttpResponse(mimetype='text/csv')
#    # response['Content-Disposition'] = 'attachment; filename=somefilename.csv'
#    writer = csv.writer(response)
#
#    reader = csv.reader(open("testcsv.data"), delimiter=",")
#    # for title, year, director in reader:
#    # print year, title
#    # writer.writerow([year,title])
#    for adr, acry, apry, cag, a1wy, a1my, a6my in reader:
#      print adr, acry
#      writer.writerow([adr, acry])
#    return response

@login_required
def searchs(request, template_name="beacon/search_list.html"):
    query = request.GET.get("query", "")
    username = getUserName(request) 
    if query == "": 
        return render_to_response(template_name, {
            'current_path': request.get_full_path(),
        }, context_instance=RequestContext(request))
#    query = urllib2.quote(query.encode("utf8"))
#    query = to_unicode_or_bust(query)
#    query = urllib2.quote(query.encode("utf8")) 
    urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&length=1100&query=" + urllib2.quote(query.encode("utf8"))  
    udata=getDataByUrl(urlstr)
#    print urlstr
#    start = time.clock() 
#    udata = loadFromUrl(urlstr) 
#    urlstop = time.clock()  
#    diff = urlstop - start  
##    print "loadFromUrl(%s) has taken %s" % (urlstr,str(diff))
#    docs = []
#    if udata.has_key("docs"):
#        for doc in udata["docs"]:
#            doc["id"] = getHashid(doc["url"])
#            doc["create_time"] = timeElaspe(doc["create_time"])
#            docs.append(doc)
#        udata["docs"] = docs
#    udata["docs"] = [procDoc(doc) for doc in udata["docs"] ]  
    return render_to_response(template_name, {
        'current_path': request.get_full_path(),
#        'udata': udata["docs"][0]["title"],  
        'udata': udata,
        "query":query,
    }, context_instance=RequestContext(request)) 

@login_required
def globaltag(request, template_name="beacon/related_list.html"):
    globaltag = request.GET.get("globaltag", "") 
    quantity = log_typer(request, "globaltag", globaltag)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    username = getUserName(request)
    globaltag = urllib2.quote(globaltag.encode("utf8")) 
    urlstr = "http://www.gxdx168.com/research/svc?globaltag=" + globaltag
    
    otype = request.GET.get("o", "")
    if otype=="service":
        udata=getDataByUrl(urlstr,True) 
        start = request.GET.get("start", "0")
        num = request.GET.get("num", "50")
        tagnum = request.GET.get("tagnum", "10")
        udata["docs"] = udata["docs"][int(start): int(start) + int(num)] 
        udata["tags"] = udata["tags"][0: int(tagnum)] 
        udata["total"] = str(udata["total"])
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    
    udata=getDataByUrl(urlstr)
    return render_to_response(template_name, {
        'udata': udata,
        "user": request.user,
    }, context_instance=RequestContext(request)) 
    
@login_required
def todaynews(request, template_name="beacon/related_list.html"):
    otype = request.GET.get("o", "")
    quantity = log_typer(request, "todaynews", "今闻观止")
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>') 
    username = getUserName(request)
    urlstr = "http://www.gxdx168.com/research/svc?o=1&page=0&length=90"
    
    if otype=="service":
        udata=getDataByUrl(urlstr,True) 
        start = request.GET.get("start", "0")
        num = request.GET.get("num", "50")
        tagnum = request.GET.get("tagnum", "10")
        udata["docs"] = udata["docs"][int(start): int(start) + int(num)] 
        udata["tags"] = udata["tags"][0: int(tagnum)] 
        udata["total"] = str(udata["total"])
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    else:
        udata=getDataByUrl(urlstr) 
    tags = []
    if udata.has_key("tags"):
        tags = udata["tags"] 
#    primarytags = [ "央 行","银 行","保 险","证 券","大 盘","基 金","信 托","外 汇","黄 金","债 券",
#"期 货","理 财","电 商","电 信","房 地 产","能 源","煤 炭","航 空","铁 路",
#"汽 车","钢 铁","船 舶","医 药","食 品","白 酒","茶 叶","蔬 菜","鞋 业","农 村",
#"林 业","土 地","畜 牧 业","渔 业","旅 游","文 化","电 影","传 媒","贸 易","欧 洲",
#"美 联 储","环 保","就 业","城 镇 化"
#                  ]
#    primarytags = [tag.decode("utf8") for tag in primarytags ]
#    tags = [tag for tag in tags if tag not in primarytags]
#    tags = primarytags + tags
#    udata["tags"] = primarytags
    udata["tags"] = tags[0:30]
    return render_to_response(template_name, {
        'udata': udata,
        "user": request.user,
    }, context_instance=RequestContext(request)) 

@login_required
def relatednews(request, template_name="beacon/related_list.html"):
    relatedid = request.GET.get("relatedid", "") 
    localtag = request.GET.get("localtag", "")
    if localtag !="":
        title = request.GET.get("title", relatedid)
        quantity = log_typer(request, "relatednews", title+"|-|"+localtag)
    else:
        host = request.GET.get("host", relatedid)
        title = request.GET.get("title", relatedid)
        quantity = log_typer(request, "relatednews", title+"|-|"+host)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    username = getUserName(request)
    if localtag !="":
        localtag = urllib2.quote(localtag.encode("utf8"))
        urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&relatedid="+relatedid+"&localtag=" + localtag
    else:
        urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&relatedid=" + relatedid
         
    otype = request.GET.get("o", "")
    if otype=="service":
        udata=getDataByUrl(urlstr,True) 
        start = request.GET.get("start", "0")
        num = request.GET.get("num", "50")
        tagnum = request.GET.get("tagnum", "10")
        udata["docs"] = udata["docs"][int(start): int(start) + int(num)] 
        udata["tags"] = udata["tags"][0: int(tagnum)] 
        udata["total"] = str(udata["total"])
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    udata=getDataByUrl(urlstr) 
    
    return render_to_response(template_name, {
        'username': username,
        'udata': udata,
        "user": request.user,
    }, context_instance=RequestContext(request)) 
     
@login_required
def load_beacons(request): 
    quantity = log_typer(request, "load_beacons", "None") 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5") 
    username = request.GET.get("u", getUserName(request))
    
    beacon_json = {}
    beacon_list = []
    mybeaconids = []
    fllwbeaconids = []
    group_list=[]
    groupobj={} 
#    if orderby=="tms":
#        sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#    elif orderby=="fllw":
#        sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#    elif orderby=="news":
#        sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1)  
    beacons = r.smembers("usr:" + username+":fllw") 
    for beastr in beacons:
#        if r.hget("bmk:" + beaid, "crt_usr") != username:
#            continue
        beausr,beaid=beastr.split("|-|")
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid)
        if not beaobj.has_key("ttl"):#如果该灯塔已经被删除了(脏数据)
            continue
        beaobj["news_cnt"] = "1"
#        beaobj["desc"] = beaobj["ttl"]
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj["beaconid"] = beaid
        beacon_list.append(beaobj)
        fllwbeaconids.append(beaid)
        
    mybeaconids = r.smembers("bmk:" + username)
    for beaid in mybeaconids:  
        beaobj = r.hgetall("bmk:" + username + ":" + beaid)
        if not beaobj.has_key("ttl"):#如果该灯塔已经被删除了(脏数据)
            continue
        beaobj["news_cnt"] = "1"
#        beaobj["desc"] = beaobj["ttl"]
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + username + ":" + beaid+":fllw"))
        beaobj["beaconid"] = beaid
        beacon_list.append(beaobj) 
        
    beacon_list = beacon_list[int(start): int(start) + int(num)]     
    beacon_json["message"] = ""
    beacon_json["total"] = str(len(beacon_list))
    beacon_json["beacons"] = beacon_list  
    groupobj["beaconids"] = ",".join(fllwbeaconids)
    groupobj["groupid"] = getHashid("myFllw")
    groupobj["groupname"] = "myFllw"
    group_list.append(groupobj)
    groupobj={}
    groupobj["beaconids"] = ",".join(mybeaconids)
    groupobj["groupid"] = getHashid("myCre")
    groupobj["groupname"] = "myCre"
    group_list.append(groupobj)
    groupobj={}
    groupobj["beaconids"] = ",".join(set(fllwbeaconids).union(mybeaconids))
    groupobj["groupid"] = getHashid("All")
    groupobj["groupname"] = "All"
    group_list.append(groupobj)
    print groupobj["beaconids"] 
    beacon_json["groups"] = group_list
    
    beacon_json["t"] = str(time.time())
    if len(beacon_list) < num:
        beacon_json["havemore"] = "false"
    else:
        beacon_json["havemore"] = "true" 
    # [{"name":"beaconA","hasdoc":"true"},{"name":"beaconB","hasdoc":"false"}]
#    beacons = [beacontran(beaid, similarid) for beaid in beacons ]
#    rtstr = "".join(i for i in json.dumps(beacon_json) if ord(i)<128 and ord(i)>20)
#    print rtstr
#    rtstr = json.dumps(beacon_json).replace("\t", "").replace("\n", "")
    return HttpResponse(json.dumps(beacon_json), mimetype="application/json")

# @login_required
def listbeacons_service(request):
    orderby = request.GET.get("orderby", "news")
    beaconname=request.GET.get("beaconname", "")
    username = request.GET.get("u", getUserName(request))
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5")
    btype = request.GET.get("btype", "notfllw")#fllw,notfllw,all
    sharebeacons=[]
    sharebeacon_list=[]
    mybeacons=[]
    robj={}
    beaobj={}
    
#     if orderby=="tms":
#         sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#     elif orderby=="fllw":
#         sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#     elif orderby=="news":
#         sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1) 
    sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
        
#     mybeacons = r.smembers("usr:" + username+":fllw")
    mybeacons = r.zrevrange("usr:" + username+":fllw",0,-1)
    for beaconstr in mybeacons:
        beausr,beaid = beaconstr.split("|-|")
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj["beaconid"] = beaid 
        beaobj["isfllw"] = "true" 
        if not beaobj.has_key("ttl"):
            continue
        if not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询) 
            beaconttl = beaobj["ttl"]
            beaconname=to_unicode_or_bust(beaconname)
            beaconttl=to_unicode_or_bust(beaconttl)  
            if re.search(beaconname,beaconttl): 
                sharebeacon_list.append(beaobj)
        else:
            sharebeacon_list.append(beaobj)
        
    sharebeacons =  listsub(sharebeacons,mybeacons)
    for beaconstr in sharebeacons:
        beausr,beaid = beaconstr.split("|-|")
#        print "bmk:" + beausr + ":" + beaid +"==="+str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj["beaconid"] = beaid
        beaobj["isfllw"] = "false"
        if not beaobj.has_key("ttl"):
            continue
        if not beaconname=="":#根据beaconid取所有同名的灯塔(如果是查询)  
            beaconttl = beaobj["ttl"] 
#                 print isinstance( beaconname, unicode )
#                 print isinstance( beaconttl, unicode )
            beaconname=to_unicode_or_bust(beaconname)
            beaconttl=to_unicode_or_bust(beaconttl) 
#                 print beaconname.encode("gbk"),":",beaconttl.encode("gbk")
            if re.search(beaconname,beaconttl):
#                     print beaconname,"==",beaconttl
                sharebeacon_list.append(beaobj)
        else:
            sharebeacon_list.append(beaobj)
#         if r.sismember("usr:"+username+":fllw",beaconstr):#频道已经被该用户关注
#         if r.zscore("usr:"+username+":fllw",beaconstr) is not None:#频道已经被该用户关注
#             if btype == "notfllw":#选择还未被用户关注的频道
#                 continue
#             beaobj["isfllw"] = "true"
#         else:#频道尚未被该用户关注
#             if btype == "fllw":#选择的是用户已经被关注的频道
#                 continue
#             beaobj["isfllw"] = "false"
#         if beaconstr in mybeacons: 
#             continue
        

    sharebeacon_list = sharebeacon_list[int(start): int(start) + int(num)]
    robj["success"] = 'true'
    robj["message"] = "success to featch data"  
    robj["total"] = str(len(sharebeacon_list)) 
    robj["beacons"] = sharebeacon_list
    return HttpResponse(json.dumps(robj), mimetype="application/json")
            
@login_required
def fllowbeacon_service(request):
    heartusr = request.GET.get("beaconusr", "")
    heartid = request.GET.get("beaconid", "")  
    heartopt = request.GET.get("fllwopt", "")
    username = request.GET.get("u", getUserName(request))
    robj={}
    beaobj={}
    fllwkey=""
    if r.exists("bmk:" + heartusr + ":" + heartid):
        fllwkey="bmk:" + heartusr + ":" + heartid+":fllw"
    else:
        robj["success"] = 'false'
        robj["message"] = "beacon with beaconusr:%s and beaconid:%s is not exist" %(heartusr,heartid)
        robj["beacon"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
        
    if heartopt=="remove":
        r.srem(fllwkey,username)
#         r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
        r.zrem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
        r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
#            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,-1)
    elif heartopt== "add":
        r.sadd(fllwkey,username)
#         r.sadd("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
        r.zadd("usr:" + username+ ":fllw" ,time.time(), heartusr+"|-|"+heartid)
        r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
    
    robj["success"] = 'true'
    robj["message"] = "success %s beacon" %(heartopt)
    beaobj = r.hgetall("bmk:" + heartusr + ":" + heartid)
    beaobj["news_cnt"] = "1"
    beaobj["fllw_cnt"] = str(r.scard(fllwkey))
    beaobj["beaconid"] = heartid
    robj["beacon"] = beaobj
    return HttpResponse(json.dumps(robj), mimetype="application/json")

@login_required
def load_similars(request):
    groupid = request.GET.get("groupid", "") 
    beaconid = request.GET.get("beaconid", "1968416984598300074")  
    beaconusr = request.GET.get("beaconusr", "ltb")
    obj= "all" if groupid !="" else beaconusr+":"+beaconid
    quantity = log_typer(request, "load_similars", obj) 
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
     
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5") 
    username = getUserName(request)
#     username = request.GET.get("u", getUserName(request))
    
    sim_lst=[]
    lst=[]
    beacons = []
    # modified by devwxi 临时使用..
    if groupid==getHashid("All"):
        udata = getAllBeaconDocsByUser(username,start=start ,num=num,newscnt=1)
        udata["success"] = "true"
        udata["message"] = "success return data"
        if udata.has_key("docs"):
            udata["total"] = str(len(udata["docs"]))
        else:
            udata["total"] = "0"  
        return HttpResponse(json.dumps(udata), mimetype="application/json")
    else:#取某个灯塔的新闻
        udata = buildBeaconData(beaconusr, beaconid,start=start ,end=num,isapi=True)
        r.hset("usr:"+username+":channeltms",beaconusr+":"+beaconid,time.time())
        if udata.has_key("docs"):
            udata["success"] = "true"
            udata["message"] = "success retrive data"
        else:
            udata["success"] = "false"
            udata["message"] = "no data" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
        
     

@login_required
def beaconcopy(request, template_name="beacon_new.html"):
    usr = request.GET.get("fllw", "")
    username = getUserName(request)
#    username = request.GET.get("u", username)
    otype = request.GET.get("o", "")  
    r.sunionstore("usr:"+username+":fllw","usr:"+usr+":fllw")
    r.hset("usr:"+username,"fllw_chart",usr)
    if otype == "service": 
        beacon_json={}
        beacon_list=[]
        beacons = r.smembers("usr:" + username+":fllw") 
        for beastr in beacons: 
            beausr,beaid=beastr.split("|-|")
            beaobj = r.hgetall("bmk:" + beausr + ":" + beaid)
            beaobj["news_cnt"] = "1"
            beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
            beaobj["beaconid"] = beaid
            beacon_list.append(beaobj) 
        beacon_json["message"] = "success"
        beacon_json["total"] = str(len(beacon_list))
        beacon_json["beacons"] = beacon_list  
        return HttpResponse(json.dumps(beacon_json), mimetype="application/json")
    return HttpResponseRedirect("/news/beaconnews/")
#    for bstr in beacons:
        
@login_required
def beaconfilter(request, template_name="beacon_list.html"):
    beaconid = request.GET.get("beaconid", "") 
    if beaconid == "" :
        return HttpResponseRedirect("/news/beaconlist/")
    tag_unchk = request.GET.get("tag_unchk", "")
    doc_unchk = request.GET.get("doc_unchk", "")
    username = getUserName(request)
    key = "bmk:" + username + ":" + beaconid
    r.delete(key+":tag:unchk")
    r.delete(key+":doc:unchk")
    for tagid in tag_unchk.split(','):
        r.sadd(key+":tag:unchk",tagid)
#        print "sadd tagid @[%s] %s is ok" %(tagid,key+":tag:unchk")
    for docid in doc_unchk.split(','):
        r.sadd(key+":doc:unchk",docid)
    
    saveBeacon(username,beaconid)
#        print "sadd docid @[%s] %s is ok" %(docid,key+":doc:unchk")
    return HttpResponseRedirect("/news/beaconlist/?beaconid="+beaconid)
    
@login_required
def beaconsave(request, template_name="beacon_list.html"):
    beaconid = request.GET.get("beaconid", "")
    beaconusr = request.GET.get("beaconusr", "")
    beaconkey = request.GET.get("beaconkey", "")
    beaconmindoc = request.GET.get("beaconmindoc", "")
    headlineonly = request.GET.get("headlineonly", "0")
    desc = request.GET.get("desc", "")
    beaconname = request.GET.get("beaconname", "")
    share = request.GET.get("share", "")
    if beaconname == "" :
        return HttpResponseRedirect("/news/beaconlist/")
    username = getUserName(request)
    
    quantity = log_typer(request, "beaconsave", beaconusr+":"+beaconid)
    
    beaconname = beaconname.replace(" ","")
    beaconmindoc = 0 if beaconmindoc=="" else beaconmindoc
    key = "bmk:"+beaconkey
    if beaconkey == "":# new add 
        beaconid = getHashid(beaconname)
        key = "bmk:" + beaconusr + ":" + beaconid
        r.hset(key, "id", beaconid)
        r.hset(key, "ttl", beaconname)
        r.hset(key, "desc", desc)
        r.hset(key, "crt_usr", beaconusr)
        r.hset(key, "crt_tms", time.time())
        r.hset(key, "last_touch",0) 
        r.hset(key, "last_update",0) 
        r.hset(key, "cnt",0) 
        r.hset(key, "mindoc",beaconmindoc) 
        r.hset(key, "headlineonly",headlineonly) 
        
        r.zadd("usr:" + beaconusr+":fllw",time.time(),beaconusr+"|-|"+beaconid)
        r.zadd("bmk:doc:share", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:byfllw", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:bynews",time.time() , beaconusr + "|-|" + beaconid) 
    else:
        if beaconkey != beaconusr+":"+getHashid(beaconname):# modifykeys
#             print beaconkey,beaconusr+":"+getHashid(beaconname)
            beaconid = getHashid(beaconname) 
            beaconChangeName(beaconkey,beaconusr,beaconid)
            key = "bmk:" + beaconusr + ":" + beaconid
            r.hset(key, "id", beaconid)
            r.hset(key, "ttl", beaconname)
            r.hset(key, "desc", desc)
            r.hset(key, "mindoc",beaconmindoc) 
        else:#modify desc and so on
            r.hset(key, "desc", desc)
            r.hset(key, "mindoc",beaconmindoc) 
            r.hset(key, "headlineonly",headlineonly) 
            
#     if share == "1":
# #         fllwcnt = r.scard(key+":fllw") if r.scard(key+":fllw") is not None else 0
# #         newscnt = r.hget(key,"cnt") if r.hget(key,"cnt") is not None else 0
#         r.zadd("bmk:doc:share", time.time(), beaconusr + "|-|" + beaconid)
#         r.zadd("bmk:doc:share:byfllw", fllwcnt, beaconusr + "|-|" + beaconid)
#         r.zadd("bmk:doc:share:bynews",newscnt , beaconusr + "|-|" + beaconid)
#         greeting_typer(username, "beacon_share", beaconusr)  # 保存信息到动态欢迎日志
#     elif share == "0":
#         print beaconusr + "|-|" + beaconid
#         r.zrem("bmk:doc:share", beaconusr + "|-|" + beaconid)
#         r.zrem("bmk:doc:share:bynews", beaconusr + "|-|" + beaconid)
#         r.zrem("bmk:doc:share:byfllw", beaconusr + "|-|" + beaconid)
# #    return HttpResponse("a")
    return HttpResponseRedirect("/news/beaconlist/?beaconid="+beaconid+"&beaconusr="+beaconusr)
    
@login_required
def beaconRelate(request, template_name="beacon_news.html"):
    """在搜索出来的新闻主题页面(坐标文章)下,关联一系列灯塔
    """
    beacons = request.GET.get("beacons", "") 
    checklist = request.GET.get("checklist", "") 
    similarid = request.GET.get("similarid", "")  
    
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request) 
    
    otype = request.GET.get("otype", "beacon") 
    objectid = request.GET.get("objectid", "") 
    if otype =="similar":
        print "similar"
        similarid=objectid
        urlstr = "http://www.gxdx168.com/research/svc?length=1100&similarid=" + similarid
#        return HttpResponse(objectid)
    elif otype =="related":
        print "related"  
        similarid=objectid
        urlstr = "http://www.gxdx168.com/research/svc?relatedid=" + similarid 
    elif otype =="localtag":
        similarid,localtag=objectid.split("|-|")
        localtag = urllib2.quote(localtag.encode("utf8"))
        urlstr = "http://www.gxdx168.com/research/svc?relatedid=" + similarid+"&localtag="+localtag
#        return HttpResponse(objectid)
    udata = getDataByUrl(urlstr)
    sim_docs = udata["docs"]
    beacons = beacons[0:-3] if beacons != "" else ""
    b_list = beacons.split('|-|')
#    sim_docs = saveSimilarDocs(similarid)
#    print sim_ids
    pipe = r.pipeline()
    i = 0
    for beacon in b_list:
        id = getHashid(beacon)
#        print beacon + "==" + id
        if beacon == "":
            continue
        key = "bmk:" + username + ":" + id
        pipe.zadd("bmk:doc:share", time.time(), username + "|-|" + id)
        if not r.sismember("bmk:"+username, id):
            pipe.sadd("bmk:" + username, id)
            pipe.hset(key, "ttl", beacon) 
#            pipe.hset(key, "desc", beacon)
            pipe.hset(key, "crt_usr", username)
            pipe.hset(key, "crt_tms", time.time())
            pipe.hset(key, "brk_tms", time.time())
            
        if checklist[i] == '1':  # 标签被选中
            if otype == "similar":
                pipe.sadd(key + ":doc", similarid)
                pipe.zadd(key + ":doc:tms", time.time(), similarid)
            elif otype =="related":
                pipe.sadd(key + ":doc:related", similarid)
                pipe.zadd(key + ":doc:tms", time.time(), similarid)
            elif otype =="localtag":
                pipe.sadd(key + ":doc:localtag", objectid)
                pipe.zadd(key + ":doc:tms", time.time(), similarid)
            greeting_typer(username, "beacon_save", beacon)  # 保存信息到动态欢迎日志
            for simdoc in sim_docs:
                pipe.sadd(key + ":sml", simdoc["docid"])
                pipe.zadd(key + ":sml:tms", int(simdoc["tms"]), simdoc["docid"])
        elif checklist[i] == '0':  # 标签未选中
            if otype == "similar":
                pipe.srem(key + ":doc", similarid)
            elif otype =="related":
                pipe.srem(key + ":doc:related", similarid) 
            elif otype =="localtag":
                pipe.srem(key + ":doc:localtag", objectid) 
            pipe.srem(key + ":doc:unchk", similarid)
            for simdoc in sim_docs:
                pipe.srem(key + ":sml", simdoc["docid"])
                pipe.zrem(key + ":sml:tms", simdoc["docid"])
        elif checklist[i] == '2':  # 已有标签删除
            pipe.srem("bmk:" + username, id)  # 从标签总的集合中删除该标签
            pipe.zrem("bmk:doc:share",username + "|-|" + id)
            pipe.zrem("bmk:doc:byfllw",username + "|-|" + id)
            pipe.zrem("bmk:doc:bynews",username + "|-|" + id)
            pipe.delete(key + ":doc")
            pipe.delete(key + ":doc:related")
            pipe.delete(key + ":doc:localtag")
            pipe.delete(key + ":doc:tms")
            pipe.delete(key + ":sml")
            pipe.delete(key + ":sml:tms")
#            pipe.srem(key + ":doc", similarid)#去除标签的 坐标文档
#            for simdoc in sim_docs:
#                pipe.srem(key + ":sml", simdoc["id"])
#                pipe.zrem(key + ":sml:tms", simdoc["id"])
        else:
            pass
        i = i+1
        
        pipe.execute()
    return HttpResponse("beacon relative is ok.")
#    return HttpResponseRedirect("/news/beaconinit/?similarid=" + similarid + "&title=" + title) 

@login_required
def mybeacons(request, template_name="beacon/mybeacons.html"): 
    beaconname = request.GET.get("beaconname", "")
    heartopt = request.GET.get("heartopt", "")
    heartid = request.GET.get("heartid", "")
    heartusr = request.GET.get("heartusr", "")
    orderby = request.GET.get("orderby", "tms")
    username = getUserName(request)
    userobj = request.user
    beacon_list=[]
    mybeacons=[] 
    beacon_search=[]
    beaobj={}
    myfllw_list = []
    
    if heartid !="":
        fllwkey="bmk:" + heartusr + ":" + heartid+":fllw"
        if heartopt=="remove":
            r.srem(fllwkey,username)
            r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
            r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
#            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,-1)
        elif heartopt== "add":
            r.sadd(fllwkey,username)
            r.sadd("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
            r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
#            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,1)
#            r.hincrby("bmk:" + heartusr + ":" + heartid,)
    if orderby=="tms":
        sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
    elif orderby=="fllw":
        sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
    elif orderby=="news":
        sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1)
        
    mybeacon_list = r.smembers("bmk:" + username)
        
    descstr=""
    for beastr in sharebeacons:#取所有分享的,不属于自己的,未被following的灯塔(可以follow的灯塔)
        beaconusername,beaconid=beastr.split('|-|')
        beaobj = r.hgetall("bmk:" + beaconusername + ":" + beaconid)
        if beaobj.has_key("desc"):
#            print beaobj["desc"].decode("utf8")
            descstr = beaobj["desc"].decode("utf8")[0:15]
#            print beaobj["desc"].decode("utf8")
            beaobj["desc"]= descstr
        beaobj["news_cnt"] = "1"
        beaobj["fllw_cnt"] = r.scard("bmk:" + beaconusername + ":" + beaconid+":fllw")
        beaobj["id"] = beaconid 
        if beaconid in mybeacon_list :# 自己的灯塔
            mybeacons.append(beaobj)
            continue
        if r.sismember("bmk:" + beaconusername + ":" + beaconid+":fllw",username):#已经following的灯塔
            myfllw_list.append(beaobj)  
            continue 
        
#        import re
#        if not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询)
#            print beaconname
#            print beaobj["ttl"].decode("utf8")
#            if re.search(beaconname,beaobj["ttl"].decode("utf8")):
#                beacon_search.append(beaobj) 
        import re
        if not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询)
            if beaobj.has_key("ttl"):
                beaconttl = beaobj["ttl"]
            else:
                beaconttl=""
            beaconname=to_unicode_or_bust(beaconname)
            beaconttl=to_unicode_or_bust(beaconttl) 
            if re.search(beaconname,beaconttl):
                beacon_search.append(beaobj)
                
#        if getHashid(beaconname)==beaconid:#根据beaconid取所有同名的灯塔(如果是查询)
#            beacon_search.append(beaobj)
            
        beacon_list.append(beaobj) 
    return render_to_response(template_name, {
#        'udata': udata,
        'beacons':beacon_list,
        'beacon_search':beacon_search,
        'mybeacons':mybeacons,
        'myfllws':myfllw_list,
        "user": userobj,
        "greetings":getGreeting(),
#        'shared':shared, 
    }, context_instance=RequestContext(request)) 

@login_required
def beaconnews(request,template_name="beacon/beacon_news.html"):  
    start = time.clock()
    
    beaconid = request.GET.get("beaconid", "")  
    beaconname = request.GET.get("beaconname", "")  
    beaconusr = request.GET.get("beaconusr", "")  
    orderby = request.GET.get("orderby", "tms")  
    heartopt = request.GET.get("heartopt", "")
    heartid = request.GET.get("heartid", "")
    heartusr = request.GET.get("heartusr", "")
    
    logobj = "ordey by "+orderby
    if beaconid !="":
        logobj= r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl")
    elif heartid !="":
        beaconname = r.hget("bmk:" + heartusr + ":" + heartid, "ttl")
        beaconname = to_unicode_or_bust(beaconname)
        logobj = heartopt+" --> "+ heartusr+":"+beaconname
    elif not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询)
        beaconname=to_unicode_or_bust(beaconname)
        logobj = "query : "+beaconname
    else :
        logobj="all"
    
    quantity = log_typer(request, "beaconnews", logobj)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    userobj = request.user
    username = getUserName(request)
    beaobj = {}
    mybeacon_list = []
    myfllw_list = []
    sharebeacon_list = []
    sharebeacons=[]
    mybeacons = []
    beacon_search=[]
    request.session["otype"] = "beaconnews"
    
    udata = {}
    shared = ""
    
    if heartid !="":
        beaconname =""
        if r.exists("bmk:" + heartusr + ":" + heartid):
            fllwkey="bmk:" + heartusr + ":" + heartid+":fllw"
            if heartopt=="remove":
                r.srem(fllwkey,username)
#                 r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
                r.zrem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
                r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
    #            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,-1)
            elif heartopt== "add":
                r.sadd(fllwkey,username)
#                 r.sadd("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
                r.zadd("usr:" + username+ ":fllw" , time.time(),heartusr+"|-|"+heartid)
                r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),heartusr+"|-|"+heartid)
            
#     if orderby=="tms":
#         sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#     elif orderby=="fllw":
#         sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#     elif orderby=="news":
#         sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1)
    sharebeacons = r.zrevrange("bmk:doc:share",0,-1) 
#     mybeacons = r.smembers("usr:" + username+":fllw") 
    mybeacons = r.zrevrange("usr:" + username+":fllw",0,-1)
    
    for beaconstr in mybeacons:
        beausr,beaid = beaconstr.split("|-|") 
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = r.scard("bmk:" + beausr + ":" + beaid+":fllw")
        beaobj["id"] = beaid
        beaobj["new_cnt"] = getBeaconNewsCnt(username,beausr,beaid)
        if not beaobj.has_key("ttl"):#如果该灯塔已经被删除了(脏数据)
            continue
        myfllw_list.append(beaobj)
    
    sharebeacons = listsub(sharebeacons,mybeacons) 
    for beaconstr in sharebeacons:
        beausr,beaid = beaconstr.split("|-|")
#        print "bmk:" + beausr + ":" + beaid +"==="+str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = r.scard("bmk:" + beausr + ":" + beaid+":fllw")
        beaobj["new_cnt"] = getBeaconNewsCnt(username,beausr,beaid)
        beaobj["id"] = beaid
        if not beaobj.has_key("ttl"):#如果该灯塔已经被删除了(脏数据)
            continue
        sharebeacon_list.append(beaobj)
          
        if not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询)
            if beaobj.has_key("ttl"):
                beaconttl = beaobj["ttl"]
            else:
                continue
            beaconname=to_unicode_or_bust(beaconname)
            beaconttl=to_unicode_or_bust(beaconttl,"utf8") 
            if re.search(beaconname,beaconttl):
                beacon_search.append(beaobj) 
                
    if beaconid != "":  
        udata = buildBeaconData(beaconusr, beaconid,start=0 ,end=100) 
        beaconname = r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl") 
        r.hset("usr:"+username+":channeltms",beaconusr+":"+beaconid,time.time())#增加用户关于该频道的最后跟新时间
        cnt = len(udata["docs"]) if udata.has_key("docs") else 0
        r.hset("bmk:" + beaconusr + ":" + beaconid,"cnt",cnt)
    else:  
        udata = getAllBeaconDocsByUser(username,newscnt=5)
#         udata["simdocs"]=udata.pop("docs") 
        
    return render_to_response(template_name, {
        'udata': udata,
        'mybeacons':mybeacon_list,
        'myfllw_list':myfllw_list,
        'sharebeacons':sharebeacon_list,
        'beaconid':beaconid,#当前灯塔的ID
        'beaconusr':beaconusr,#当前灯塔的ID
        'beaconname':beaconname,#当前灯塔的名称
        'beacon_search':beacon_search,
        "greetings":getGreeting(),
        'orderby':orderby,
        'username':username,
    }, context_instance=RequestContext(request))    
#    return HttpResponseRedirect("/news/beaconlist/?new")

@login_required
def beaconlist(request, template_name="beacon/beacon_list.html"): 
    beaconid = request.GET.get("beaconid", "")  
    beaconusr = request.GET.get("beaconusr", "")
    userobj = request.user
#     if userobj.is_anonymous():  # 用户未登录
#         return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    beacon_json = {}
    beacon_list = []
    
    udata = {}
    beacondesc = ""
    beaconname = "" 
    beaconmindoc = 0
    headlineonly = "0"
    if beaconid != "":  
        udata = buildBeaconData(beaconusr, beaconid)
        beacondesc = r.hget("bmk:" + beaconusr + ":" + beaconid, "desc") 
        beaconname = r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl") 
        beaconmindoc = r.hget("bmk:" + beaconusr + ":" + beaconid, "mindoc") 
        beaconmindoc = 0 if beaconmindoc is None else beaconmindoc
        headlineonly = r.hget("bmk:" + beaconusr + ":" + beaconid, "headlineonly") 
        headlineonly = "0" if headlineonly is None else headlineonly
#         shared = False if r.zrank("bmk:doc:share", beaconusr + "|-|" + beaconid) is None else True
#         r.hset("bmk:" + beaconusr + ":" + beaconid,"cnt",len(udata["docs"]))

#     beacons = r.smembers("bmk:" + username)
    beacons = r.zrevrange("bmk:doc:share",0 ,-1)
#     print beacons
    for beaconstr in beacons:
        busr,bid = beaconstr.split("|-|")
        beaobj = r.hgetall("bmk:" + busr + ":" + bid) 
        beaobj["id"] = bid
        beaobj["crt_usr"] = busr
#         beaobj["shared"] = False if r.zrank("bmk:doc:share", beaconusr + "|-|" + beaconid) is None else True
        beacon_list.append(beaobj)   
    return render_to_response(template_name, {
        'current_path': request.get_full_path(),
        'udata': udata,
        'beacons':beacon_list,
        'beaconid':beaconid,#当前灯塔的ID
        'beacondesc':beacondesc,#当前灯塔的备注
        'beaconname':beaconname,#当前灯塔的名称 
        'beaconusr':beaconusr,#当前灯塔的名称  
        'beaconmindoc':beaconmindoc,
        'headlineonly':headlineonly,
        "user": userobj,
    }, context_instance=RequestContext(request)) 

@login_required
def beacondelete(request, template_name="beacon/beacon_list.html"):  
    username = getUserName(request)  
    beaconusr = request.GET.get("beaconusr", "")
    beaconid = request.GET.get("beaconid", "")
#     print beaconusr,beaconid
    key = "bmk:" + beaconusr + ":" + beaconid
    channel = r.hget(key,"ttl")
    quantity = log_typer(request, "beacondelete", to_unicode_or_bust(channel))
    r.zrem("bmk:doc:share",beaconusr+"|-|"+beaconid) 
    r.zrem("bmk:doc:share:byfllw",beaconusr+"|-|"+beaconid) 
    r.zrem("bmk:doc:share:bynews",beaconusr+"|-|"+beaconid)
    r.zrem("usr:" + beaconusr+":fllw",beaconusr+"|-|"+beaconid)
    key = "bmk:"+beaconusr+":"+beaconid
    for usr in r.smembers(key+":fllw"):
        r.zrem("usr:" + usr+":fllw",beaconusr+"|-|"+beaconid)
    r.delete(key + ":doc:tms")
    r.delete(key + ":fllw")
    
    return HttpResponseRedirect("/news/beaconlist/")
        
@login_required
def listSimilarDoc(request, template_name="beacon/beacon_init.html"):
    beaconid = request.GET.get("beaconid", "")
    similarid = request.GET.get("similarid", "") 
    title = request.GET.get("title", "") 
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request) 
    
    udata = buildBeaconData(username, beaconid)
    
    beacons = r.smembers("bmk:" + username)
    beacons = [beacontran(username, beaid, similarid) for beaid in beacons]
#    beacons = [beacontran(beaid, similarid) for beaid in beacons if r.hget("bmk:" + beaid, "crt_usr") == username]
    
    return render_to_response(template_name, {
        'current_path': request.get_full_path(),
#        'udata': udata["docs"][0]["title"],  
        'udata': udata,
        'beacons':beacons,
        'similarid':similarid,
        'title':title,
        "user": userobj,
    }, context_instance=RequestContext(request)) 
     
@login_required
def feedbacks(request, template_name="beacon/feedback_list.html"):
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request) 
    
    feedbacks = r.lrange("feedback", 0, -1)
    print feedbacks
    feedbacks = [json.loads(fee) for fee in feedbacks ]
    return render_to_response(template_name, {  
        "feedbacks": feedbacks,
        "user": userobj,
        'current_path': request.get_full_path(),
    }, context_instance=RequestContext(request))
    
@login_required
def admin(request, template_name="beacon/admin.html"):
#    user_list = [user.replace(":ppl:uptms", "") for user in user_list ]
#    user_list = [user.replace("usr:", "") for user in user_list ]
    otype = request.GET.get("otype", "user")
    query = request.GET.get("query", "")
    query = query.replace(" ","")
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request)
    
    if username not in ["wxi","sj","ltb"]:#
        return HttpResponse('<h1>只有管理用户才能访问该功能..</h1>')
#    user_list = r.keys("usr:*:ppl:uptms")
    usrlst = []
    if otype=="log":
        userinfos= r.zrevrange("log",0,1500)
        for userinfo in userinfos:
#            print userinfo
            usr=json.loads(userinfo)  
            usr["act_tms"] = getTime(usr["tms"])
#            if usr["ip"] not in ["203.208.60.217","203.208.60.218","203.208.60.219","123.125.71.38"]:
            if query =="" :
                usrlst.append(usr)
            elif usr["ip"] == query or usr["usr"] == query:
                usrlst.append(usr)
    else:
        userinfos = r.hgetall("usrlst")
#        print userinfos
        for user,userinfo in userinfos.items(): 
            usr=json.loads(userinfo)  
            usr["act_tms"] = getTime(usr["tms"])
            usrlst.append(usr)
        usrlst = sorted(usrlst,key=lambda l:l["tms"],reverse = True)
#    print request
    return render_to_response(template_name, { 
        "usrlst": usrlst,
        "user": userobj,
        "otype": otype,
        'current_path': request.get_full_path(),
    }, context_instance=RequestContext(request))

@login_required
def sendemailforbeacon(request):
    username = getUserName(request)
    if username not in ["wxi","sj","ltb"]:#
        return HttpResponse('<h1>只有管理用户才能访问该功能..</h1>')
    hourbefore = request.GET.get("hourbefore", "8")
    beaconid=request.GET.get("beacon", "allbeacons")
    user=request.GET.get("u", username)
    
    pushQueue("sendemail", user, "bybeacon", tag=hourbefore, similarid=beaconid)
    return HttpResponse("sendemail is okay.")
    
    
@login_required
def sendemailfornews(request):
    print "===sendemailfornews==="
    
    username = getUserName(request)  
    usr_email = r.hget("usr:"+username,"email")
    groupname = request.GET.get("group", "all")
    groupemail = ",".join(r.zrevrange("usr:"+username+":buddy:"+groupname,0,-1))
    emails = request.GET.get("emails", "")
    docids = request.GET.get("docids", "")
    otype = request.GET.get("o", "")
     
    
    robj = {}
    if emails== "":
        robj["message"] ="email must be not null !"
        robj["success"] ="failed"
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    
    quantity = log_typer(request, "sendemailfornews", emails+"->"+docids)
#     if quantity > QUANTITY:
#         return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    def pushqueue(emails,docids):
        for email,docid in zip( emails.split(","),docids.split(";") ):
            pushQueue("sendemail", username, "byemail", tag=email, similarid=docid)
            
    if otype=="service":
        if emails != "":
#             pushQueue("sendemail", username, "byemail", tag=emails, similarid=docids.replace(",",";"))
            pushqueue(emails,docids.replace(",",";"))
            robj["message"] = "send email to:"+emails 
        else:
#             pushQueue("sendemail", username, "byemail", tag=usr_email, similarid=docids.replace(",",";"))
            pushqueue(usr_email,docids.replace(",",";"))   
            robj["message"] = "send email to:"+usr_email
        if groupname !="": 
            robj["group"] = groupname
        robj["success"] = 'true'
        robj["docid"] = docids
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    
    if emails != "":
        sendemailbydocid(emails,docids)
    else: 
        sendemailbydocid(usr_email,docids)
#    urlstr = "http://www.gxdx168.com/research/svc?docid=" + docids
#    udata=getDataByUrl(urlstr)
#    if udata.has_key("docs"):
#        for doc in udata["docs"]:
#            title = doc["title"]
#            content= doc["text"] 
#            content+="\r\n\r\n"+doc["url"]
#            sendemail(content,usr_email,title)
     
    return HttpResponse("sendemail is okay.")
    
@login_required
def captchalist(request, template_name="beacon/captcha.html"):
    captchaid = request.GET.get("captchaid", "")
    if captchaid != "":
        quantity = log_typer(request, "sendemail", captchaid)
    else:
        quantity = log_typer(request, "captchalist", captchaid)
    if quantity > QUANTITY:
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    if captchaid != "":
        r.hset("captcha:"+captchaid,"issendmail",True)
        username = r.hget("captcha:"+captchaid,"crt_usr")
        usr_email = r.hget("usr:"+username,"email")
        url= "http://"+request.META['HTTP_HOST']+"/apply/?captcha="+captchaid 
#        content=username+""",您好!\r\n欢迎您的注册,在访问过程中有任何疑问及建议可以给我们邮件或者在网站中提交建议,\r\n
#        现在,您可以邀请您的朋友们通过以下链接来指极星注册:\r\n  """.decode("utf8")+url
        content=username+",这是来自指极星的邀请，欢迎！\r\n\r\n指极星，帮助您在浩瀚空间中发现您关注的资讯。\r\n\r\n邀请码：".decode("utf8")+captchaid
        content+="\r\n\r\n点击加入".decode("utf8")+url+" ，主观、客观、达观的共同探索。".decode("utf8")
        sendemail(content,usr_email)
        return HttpResponseRedirect("/news/captchalist/")
#    print request
    captchas = r.keys("captcha:*")
    captchaobjs = []
    cdata={}
    for cap in captchas:
        cdata = r.hgetall(cap)
        tms= cdata["crt_tms"] if cdata.has_key("crt_tms") else "0"
        cdata["id"] = cap.replace("captcha:","")
        cdata["crt_tms"]=getTime(tms)
        cdata["tms"]=tms
        captchaobjs.append(cdata)
    captchaobjs = sorted(captchaobjs,key=lambda l:l["tms"],reverse = True)
    return render_to_response(template_name, { 
        "captchas": captchaobjs,
    }, context_instance=RequestContext(request))
    
# def daemonStart(request):
#    username = getUserName(request.user)
#    if not username == "wxi":
#        return HttpResponse(username+",only wxi can do this")
#    daemon = daemonProcess.DaemonProcess('/tmp/daemon-example.pid')
#    daemon.start()
#    return HttpResponse("daemon is start....") 
#
# def daemonStop(request):
#    username = getUserName(request.user)
#    if not username == "wxi":
#        return HttpResponse(username+",only wxi can do this")
#    daemon = daemonProcess.DaemonProcess('/tmp/daemon-example.pid')
#    daemon.stop()
#    return HttpResponse("daemon is stop....") 
#
# def daemonRestart(request):
#    username = getUserName(request.user)
#    if not username == "wxi":
#        return HttpResponse(username+",only wxi can do this")
#    daemon = daemonProcess.DaemonProcess('/tmp/daemon-example.pid')
#    daemon.restart()
#    return HttpResponse("daemon is restart....")  
 
# @login_required
# def beaconinit(request, template_name="beacon/beacon_init.html"):
#     otype = request.GET.get("otype", "similar") 
#     similarid = request.GET.get("similarid", "")
#     relatedid = request.GET.get("relatedid", "")
#     localtag = request.GET.get("localtag", "") 
#     userobj = request.user
#     username = getUserName(request) 
#     
#     objectid =""
#     udata = {}
#     if otype=="similar":
#         urlstr = "http://www.gxdx168.comcom/research/svc?length=1100&similarid=" + similarid
#         objectid=similarid 
#     elif otype =="related": 
#         urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&relatedid=" + relatedid
#         objectid = relatedid
#         similarid = relatedid
#     elif otype =="localtag":
# #        localtag = urllib2.quote(localtag.encode("utf8"))
#         urlstr = "http://www.gxdx168.com/research/svc?u=" + username + "&relatedid="+relatedid+"&localtag=" + urllib2.quote(localtag.encode("utf8"))
#         objectid=relatedid+"|-|"+localtag
#         similarid = relatedid
#         
#     udata=getDataByUrl(urlstr) 
#     beacons = r.smembers("bmk:" + username)
#     # [{"name":"beaconA","hasdoc":"true"},{"name":"beaconB","hasdoc":"false"}]
#     beacons = [beacontran(username, beaid, similarid) for beaid in beacons ]
# #    udata["docs"] = [procDoc(doc) for doc in udata["docs"] ]  
# #    print objectid
#     return render_to_response(template_name, {
#         'current_path': request.get_full_path(),
# #        'udata': udata["docs"][0]["title"],  
#         'udata': udata,
#         'beacons':beacons,
#         'objectid':objectid,
#         'otype':otype,
#         "user": userobj,
#     }, context_instance=RequestContext(request)) 
