#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
import json, urllib2, urllib, redis
import csv, string, re, sys, time, numpy
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required, permission_required
from django.template.defaultfilters import length
from mybonds.apps.newspubfunc import *
from mybonds.apps.geeknews import *
# import mybonds.apps.geeknews.daemonProcess as daemonProcess


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
def init(request, oper): 
    def init_bmk_fllwkeys():
        fllwkeys = r.keys("bmk:*:fllw")
        print fllwkeys
        for fllwkey in fllwkeys:
            bmk, usr, id, fllw = fllwkey.split(":")
            print bmk, usr, id, fllw 
            print r.scard(fllwkey)
            r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), usr + "|-|" + id)
    def init_bmk_newskey():
        keystrs = r.zrevrange("bmk:doc:share", 0, -1)
        for keystr in keystrs:
            usr, id = keystr.split("|-|")
            cnt = r.hget("bmk:" + usr + ":" + id, "cnt") if r.hget("bmk:" + usr + ":" + id, "cnt") is not None else 0
            r.zadd("bmk:doc:share:bynews", cnt, keystr)
    if oper == "init_bmk_fllwkeys":
        init_bmk_fllwkeys()
    elif oper == "init_bmk_newskey":
        init_bmk_newskey()
    return HttpResponse("ok")
    
# @log_typer        
@login_required
def test(request):
    print "---------geeknews/test---------"
    return HttpResponse("ok")

@login_required
def feedback_reply(request):
    content = request.GET.get("content", "")
    quantity = log_typer(request, "feedback", content)
    if quantity > getsysparm("QUANTITY"):
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

@login_required
def research(request,template_name="beacon/fulltextnew.html"): 
    username = getUserName(request) 
    docid = request.GET.get("docid", "")
    name = r.hget("doc:"+docid,"name")
    quantity = log_typer(request, "reserch", name)
    if quantity > getsysparm("QUANTITY"):
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>') 
    ftxlist=[]
    fulldoc = tftxs.find_one({"_id":docid})
    if fulldoc is not None:
#         print fulldoc
        ftxlist = fulldoc["fulltext"] 
        url = fulldoc["urls"][0].split(",")[1]
    else:
        doc = rdoc.hgetall("doc:"+docid)
        ftxlist.append(doc["text"])
        url = doc["url"] if doc.has_key("url") else ""
    return render_to_response(template_name, {
        'ftxlist': ftxlist, 
        'url': url,
        'tempparmsobj':r.hgetall("tempparms"),
    }, context_instance=RequestContext(request))    

# @login_required
# def overview(request):
#     print "---------geeknews/overview---------"
#     pass

# @login_required
# def history(request):
#     print "---------geeknews/history---------"
#     pass
    
# @login_required
# def navi(request, template_name="geeknews.html"):
#     print "---------geeknews/foucs---------"
#     pass

# @login_required
# def recomm(request, template_name="geeknews.html"):
#     print "geeknews/recomment" 
#     pass
#     
# 
# @login_required
# def tagdoc(request, tag, template_name="geeknews.html"):  # 获得某个标签的关联标签信息
#     print "geeknews/tagdoc" 
#     pass

# @login_required
# def load_seeds(request):
#     pass
     
# @login_required
# def retriveData(request):
#     pass

# @login_required
# def searchs(request, template_name="beacon/search_list.html"):
#     pass
# 
# @login_required
# def globaltag(request, template_name="beacon/related_list.html"):
#     pass
#     
# @login_required
# def todaynews(request, template_name="beacon/related_list.html"):
#     pass
# 
# @login_required
# def relatednews(request, template_name="beacon/related_list.html"):
#     pass
     
@login_required
def load_beacons(request): 
    quantity = log_typer(request, "load_beacons", "None") 
    if quantity > getsysparm("QUANTITY"):
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5") 
    username = request.GET.get("u", getUserName(request))
    
    beacon_json = {}
    beacon_list = []
    mybeaconids = []
    fllwbeaconids = []
    group_list = []
    groupobj = {} 
#    if orderby=="tms":
#        sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#    elif orderby=="fllw":
#        sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#    elif orderby=="news":
#        sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1)  
    beacons = r.smembers("usr:" + username + ":fllw") 
    for beastr in beacons:
#        if r.hget("bmk:" + beaid, "crt_usr") != username:
#            continue
        beausr, beaid = beastr.split("|-|")
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid)
        if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
            continue
        beaobj["news_cnt"] = "1"
#        beaobj["desc"] = beaobj["ttl"]
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid + ":fllw"))
        beaobj["beaconid"] = beaid
        beacon_list.append(beaobj)
        fllwbeaconids.append(beaid)
        
    mybeaconids = r.smembers("bmk:" + username)
    for beaid in mybeaconids:  
        beaobj = r.hgetall("bmk:" + username + ":" + beaid)
        if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
            continue
        beaobj["news_cnt"] = "1"
#        beaobj["desc"] = beaobj["ttl"]
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + username + ":" + beaid + ":fllw"))
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
    groupobj = {}
    groupobj["beaconids"] = ",".join(mybeaconids)
    groupobj["groupid"] = getHashid("myCre")
    groupobj["groupname"] = "myCre"
    group_list.append(groupobj)
    groupobj = {}
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
    beaconname = request.GET.get("beaconname", "")
    username = request.GET.get("u", getUserName(request))
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5")
    btype = request.GET.get("btype", "notfllw")  # fllw,notfllw,all
    sharebeacons = []
    sharebeacon_list = []
    mybeacons = []
    robj = {}
    beaobj = {}
    
#     if orderby=="tms":
#         sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#     elif orderby=="fllw":
#         sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#     elif orderby=="news":
#         sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1) 
    sharebeacons = r.zrevrange("bmk:doc:share", 0, -1)
        
#     mybeacons = r.smembers("usr:" + username+":fllw")
    mybeacons = r.zrevrange("usr:" + username + ":fllw", 0, -1)
    for beaconstr in mybeacons:
        beausr, beaid = beaconstr.split("|-|")
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid + ":fllw"))
        beaobj["beaconid"] = beaid 
        beaobj["isfllw"] = "true" 
        if not beaobj.has_key("ttl"):
            continue
        if not beaconname == "":  # 根据beaconid取所有同名的灯塔(如果是查询) 
            beaconttl = beaobj["ttl"]
            beaconname = to_unicode_or_bust(beaconname)
            beaconttl = to_unicode_or_bust(beaconttl)  
            if re.search(beaconname, beaconttl): 
                sharebeacon_list.append(beaobj)
        else:
            sharebeacon_list.append(beaobj)
        
    sharebeacons = listsub(sharebeacons, mybeacons)
    for beaconstr in sharebeacons:
        beausr, beaid = beaconstr.split("|-|")
#        print "bmk:" + beausr + ":" + beaid +"==="+str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid + ":fllw"))
        beaobj["beaconid"] = beaid
        beaobj["isfllw"] = "false"
        if not beaobj.has_key("ttl"):
            continue
        if not beaconname == "":  # 根据beaconid取所有同名的灯塔(如果是查询)  
            beaconttl = beaobj["ttl"] 
#                 print isinstance( beaconname, unicode )
#                 print isinstance( beaconttl, unicode )
            beaconname = to_unicode_or_bust(beaconname)
            beaconttl = to_unicode_or_bust(beaconttl) 
#                 print beaconname.encode("gbk"),":",beaconttl.encode("gbk")
            if re.search(beaconname, beaconttl):
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
    robj = {}
    beaobj = {}
    fllwkey = ""
    if r.exists("bmk:" + heartusr + ":" + heartid):
        fllwkey = "bmk:" + heartusr + ":" + heartid + ":fllw"
    else:
        robj["success"] = 'false'
        robj["message"] = "beacon with beaconusr:%s and beaconid:%s is not exist" % (heartusr, heartid)
        robj["beacon"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
        
    if heartopt == "remove":
        r.srem(fllwkey, username)
        r.zrem("usr:" + username + ":fllw" , heartusr + "|-|" + heartid)
        r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
    elif heartopt == "add":
        r.sadd(fllwkey, username) 
        r.zadd("usr:" + username + ":fllw" , time.time(), heartusr + "|-|" + heartid)
        r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
    
    robj["success"] = 'true'
    robj["message"] = "success %s beacon" % (heartopt)
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
    orderby = request.GET.get("orderby", "tms")
    ascii = request.GET.get("ascii", "1")
    obj = "all" if groupid != "" else beaconusr + ":" + beaconid
    quantity = log_typer(request, "load_similars", obj) 
    udata={}
    if quantity > getsysparm("QUANTITY"):
        udata["success"] = "false"
        udata["message"] = "you request too many times. pls wait a moments" 
        return HttpResponse(json.dumps(udata), mimetype="application/json")
     
    start = request.GET.get("start", "0")
    num = request.GET.get("num", "5") 
    username = getUserName(request)
#     username = request.GET.get("u", getUserName(request))
    
    sim_lst = []
    lst = []
    beacons = []
    # modified by devwxi 临时使用..
    if groupid == getHashid("All"):
        username = request.GET.get("u",username) 
        username = username if r.sismember("character",username) else getUserName(request)
        udata = getAllBeaconDocsByUser(username, start=start , num=num, newscnt=1)
        udata["success"] = "true"
        udata["message"] = "success return data"
        if udata.has_key("docs"):
            udata["total"] = str(len(udata["docs"]))
        else:
            udata["total"] = "0"  
#         return HttpResponse(json.dumps(udata), mimetype="application/json")
        return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
    else:  # 取某个灯塔的新闻
        try:
            udata = buildBeaconData(beaconusr, beaconid, start=int(start), end=int(num), isapi=True,orderby=orderby)
            r.hset("usr:" + username + ":channeltms", beaconusr + ":" + beaconid, time.time())
        except:
            udata["success"] = "false"
            udata["message"] = "no data" 
        else:
            udata["success"] = "true"
            udata["message"] = "success retrive data"
        return HttpResponse(json.dumps(udata,ensure_ascii=ascii=="1"), mimetype="application/json")
        
     

@login_required
def beaconcopy(request, template_name="beacon_new.html"):
    usr = request.GET.get("fllw", "")
    username = getUserName(request)
#    username = request.GET.get("u", username)
    otype = request.GET.get("o", "")  
    r.sunionstore("usr:" + username + ":fllw", "usr:" + usr + ":fllw")
    r.hset("usr:" + username, "fllw_chart", usr)
    if otype == "service": 
        beacon_json = {}
        beacon_list = []
        beacons = r.smembers("usr:" + username + ":fllw") 
        for beastr in beacons: 
            beausr, beaid = beastr.split("|-|")
            beaobj = r.hgetall("bmk:" + beausr + ":" + beaid)
            beaobj["news_cnt"] = "1"
            beaobj["fllw_cnt"] = str(r.scard("bmk:" + beausr + ":" + beaid + ":fllw"))
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
    r.delete(key + ":tag:unchk")
    r.delete(key + ":doc:unchk")
    for tagid in tag_unchk.split(','):
        r.sadd(key + ":tag:unchk", tagid)
#        print "sadd tagid @[%s] %s is ok" %(tagid,key+":tag:unchk")
    for docid in doc_unchk.split(','):
        r.sadd(key + ":doc:unchk", docid)
    
    saveBeacon(username, beaconid)
#        print "sadd docid @[%s] %s is ok" %(docid,key+":doc:unchk")
    return HttpResponseRedirect("/news/beaconlist/?beaconid=" + beaconid)
    
@login_required
def beaconsave(request, template_name="beacon_list.html"):
    username = getUserName(request)
    if username not in ["ltb", "wxi", "sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    beaconid = request.GET.get("beaconid", "")
    beaconusr = request.GET.get("beaconusr", "")
    beacontime = request.GET.get("beacontime", "")
    beaconkey = request.GET.get("beaconkey", "")
    beaconmindoc = request.GET.get("beaconmindoc", "")
    headlineonly = request.GET.get("headlineonly", "0")
    beacontag = request.GET.get("beacontag", "0")
    desc = request.GET.get("desc", "")
    beaconname = request.GET.get("beaconname", "")
    beacondisplayname = request.GET.get("beacondisplayname", "")
    share = request.GET.get("share", "")
    if beaconname == "" :
        return HttpResponseRedirect("/news/beaconlist/")
    
    quantity = log_typer(request, "beaconsave", beaconusr + ":" + beaconid)
    
    beaconname = beaconname.replace(" ", "")
    beaconmindoc = 0 if beaconmindoc == "" else beaconmindoc
    key = "bmk:" + beaconkey
    if beaconkey == "":  # new add 
        beaconid = getHashid(beaconname)
        key = "bmk:" + beaconusr + ":" + beaconid
        r.hset(key, "id", beaconid)
        r.hset(key, "ttl", beaconname)
        r.hset(key, "name", beacondisplayname)
        r.hset(key, "desc", desc)
        r.hset(key, "crt_usr", beaconusr)
#         r.hset(key, "crt_tms", time.time())
        r.hset(key, "crt_tms", getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")) 
        r.hset(key, "last_touch", 0 ) 
        r.hset(key, "last_update", 0) 
        r.hset(key, "cnt", 0) 
        r.hset(key, "mindoc", beaconmindoc) 
        r.hset(key, "tag", beacontag) 
        r.hset(key, "headlineonly", headlineonly) 
        
        r.zadd("usr:" + beaconusr + ":fllw", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:byfllw", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:bynews", time.time() , beaconusr + "|-|" + beaconid)
        
        from mybonds.build import beaconNameHash
        beaconNameHash()
    else:
        if beaconkey != beaconusr + ":" + getHashid(beaconname):  # modifykeys
#             print beaconkey,beaconusr+":"+getHashid(beaconname)
            beaconid = getHashid(beaconname) 
            beaconChangeName(beaconkey, beaconusr, beaconid)
            key = "bmk:" + beaconusr + ":" + beaconid
            r.hset(key, "id", beaconid)
            r.hset(key, "crt_usr", beaconusr)
            r.hset(key, "crt_tms", getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")) 
            r.hset(key, "ttl", beaconname)
            r.hset(key, "name", beacondisplayname)
            r.hset(key, "desc", desc)
            r.hset(key, "mindoc", beaconmindoc) 
            r.hset(key, "tag", beacontag)
            r.zadd("bmk:doc:share", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")), beaconusr + "|-|" + beaconid)
        else:  # modify desc and so on
            r.hset(key, "crt_usr", beaconusr)
            r.hset(key, "crt_tms", getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")) 
            r.hset(key, "desc", desc)
            r.hset(key, "mindoc", beaconmindoc) 
            r.hset(key, "name", beacondisplayname)
            r.hset(key, "headlineonly", headlineonly) 
            r.hset(key, "tag", beacontag) 
            r.zadd("bmk:doc:share", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")), beaconusr + "|-|" + beaconid)
            
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
    return HttpResponseRedirect("/news/beaconlist/?beaconid=" + beaconid + "&beaconusr=" + beaconusr)
    
@login_required
def beaconRelate(request, template_name="beacon_news.html"):
    """在搜索出来的新闻主题页面(坐标文章)下,关联一系列灯塔
    """
    pass

@login_required
def mybeacons(request, template_name="beacon/mybeacons.html"): 
    beaconname = request.GET.get("beaconname", "")
    heartopt = request.GET.get("heartopt", "")
    heartid = request.GET.get("heartid", "")
    heartusr = request.GET.get("heartusr", "")
    orderby = request.GET.get("orderby", "tms")
    username = getUserName(request)
    userobj = request.user
    beacon_list = []
    mybeacons = [] 
    beacon_search = []
    beaobj = {}
    myfllw_list = []
    
    if heartid != "":
        fllwkey = "bmk:" + heartusr + ":" + heartid + ":fllw"
        if heartopt == "remove":
            r.srem(fllwkey, username)
            r.srem("usr:" + username + ":fllw" , heartusr + "|-|" + heartid)
            r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
#            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,-1)
        elif heartopt == "add":
            r.sadd(fllwkey, username)
            r.sadd("usr:" + username + ":fllw" , heartusr + "|-|" + heartid)
            r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
#            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,1)
#            r.hincrby("bmk:" + heartusr + ":" + heartid,)
    if orderby == "tms":
        sharebeacons = r.zrevrange("bmk:doc:share", 0, -1)
    elif orderby == "fllw":
        sharebeacons = r.zrevrange("bmk:doc:share:byfllw", 0, -1)
    elif orderby == "news":
        sharebeacons = r.zrevrange("bmk:doc:share:bynews", 0, -1)
        
    mybeacon_list = r.smembers("bmk:" + username)
        
    descstr = ""
    for beastr in sharebeacons:  # 取所有分享的,不属于自己的,未被following的灯塔(可以follow的灯塔)
        beaconusername, beaconid = beastr.split('|-|')
        beaobj = r.hgetall("bmk:" + beaconusername + ":" + beaconid)
        if beaobj.has_key("desc"):
#            print beaobj["desc"].decode("utf8")
            descstr = beaobj["desc"].decode("utf8")[0:15]
#            print beaobj["desc"].decode("utf8")
            beaobj["desc"] = descstr
        beaobj["news_cnt"] = "1"
        beaobj["fllw_cnt"] = r.scard("bmk:" + beaconusername + ":" + beaconid + ":fllw")
        beaobj["id"] = beaconid 
        if beaconid in mybeacon_list :  # 自己的灯塔
            mybeacons.append(beaobj)
            continue
        if r.sismember("bmk:" + beaconusername + ":" + beaconid + ":fllw", username):  # 已经following的灯塔
            myfllw_list.append(beaobj)  
            continue 
        
#        import re
#        if not beaconname == "":#根据beaconid取所有同名的灯塔(如果是查询)
#            print beaconname
#            print beaobj["ttl"].decode("utf8")
#            if re.search(beaconname,beaobj["ttl"].decode("utf8")):
#                beacon_search.append(beaobj) 
        import re
        if not beaconname == "":  # 根据beaconid取所有同名的灯塔(如果是查询)
            if beaobj.has_key("ttl"):
                beaconttl = beaobj["ttl"]
            else:
                beaconttl = ""
            beaconname = to_unicode_or_bust(beaconname)
            beaconttl = to_unicode_or_bust(beaconttl) 
            if re.search(beaconname, beaconttl):
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
def hotboard(request, template_name="beacon/hotboard.html"):
    beaconid = request.GET.get("beaconid", "")  
    beaconname = request.GET.get("beaconname", "")  
    beaconusr = request.GET.get("beaconusr", "")  
    orderby = request.GET.get("orderby", "utms")   
    beacondisname = ""
    username = getUserName(request)
    udata={}
    docbeacon_list = []
    rdbeacon_list = []
    isadmin = "1" if username in ["ltb", "wxi", "sj"] else "0"  
    
    udata = buildHotBoardData(beaconusr, beaconid, start=0, end=-1, isapi=False, orderby=orderby)
    if udata.has_key("docs"):
        beacondisname = r.hget("bmk:"+beaconusr+":"+beaconid,"name")
        for doc in udata["docs"]:
            if doc["isbeacon"] == "true":
                beaobj = r.hgetall("bmk:doc:" + doc["beaconid"])
                beaobj["id"] = doc["beaconid"]
                if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
                    logger.info("beacon not exist of doc:"+doc["beaconid"])
                    continue
                docbeacon_list.append(beaobj)
                if beaconusr =="doc":
                    break
    
    rdbeacons = r.zrevrange("usr:rd:fllw", 0, -1) 
    for beaconstr in rdbeacons:
        beausr, beaid = beaconstr.split("|-|") 
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
#         beaobj["fllw_cnt"] = r.scard("bmk:" + beausr + ":" + beaid + ":fllw")
#         beaobj["new_cnt"] = getBeaconNewsCnt(username, beausr, beaid)
        beaobj["id"] = beaid
        if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
            continue
        rdbeacon_list.append(beaobj)
    
    return render_to_response(template_name, {
        'udata': udata, 
        'beaconid':beaconid,  # 当前灯塔的ID
        'beaconusr':beaconusr,  # 当前灯塔的ID
        'beaconname':beaconname,  # 当前灯塔的名称
        'beacondisname':beacondisname,  # 当前灯塔的名称
        'rdbeacon_list':rdbeacon_list,
        'docbeacon_list':docbeacon_list,
#         "greetings":getGreeting(),
        'orderby':orderby,
        'isadmin':isadmin,
        'username':username,
    }, context_instance=RequestContext(request))    

@login_required
def beaconnews(request, template_name="beacon/beacon_news.html"):  
    start = time.clock()
    
    beaconid = request.GET.get("beaconid", "")  
    beaconname = request.GET.get("beaconname", "")  
    beaconusr = request.GET.get("beaconusr", "")  
    orderby = request.GET.get("orderby", "tms")  
    heartopt = request.GET.get("heartopt", "")
    heartid = request.GET.get("heartid", "")
    heartusr = request.GET.get("heartusr", "")
    beacondisname = ""
    
    logobj = "ordey by " + orderby
    if beaconid != "":
        logobj = r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl")
    elif heartid != "":
        beaconname = r.hget("bmk:" + heartusr + ":" + heartid, "ttl")
        beaconname = to_unicode_or_bust(beaconname)
        logobj = heartopt + " --> " + heartusr + ":" + beaconname
    elif not beaconname == "":  # 根据beaconid取所有同名的灯塔(如果是查询)
        beaconname = to_unicode_or_bust(beaconname)
        logobj = "query : " + beaconname
    else :
        logobj = "all"
    
    quantity = log_typer(request, "beaconnews", logobj)
    if quantity > getsysparm("QUANTITY"):
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    
    username = getUserName(request)
    isadmin = "1" if username in ["ltb", "wxi", "sj"] else "0"  
    
    beaobj = {}
    mybeacon_list = []
    myfllw_list = []
    sharebeacon_list = []
    sharebeacons = []
    mybeacons = []
    beacon_search = []
    request.session["otype"] = "beaconnews"
    
    udata = {}
    shared = ""
    
    if heartid != "":
        beaconname = ""
        if r.exists("bmk:" + heartusr + ":" + heartid):
            fllwkey = "bmk:" + heartusr + ":" + heartid + ":fllw"
            if heartopt == "remove":
                r.srem(fllwkey, username)
#                 r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
                r.zrem("usr:" + username + ":fllw" , heartusr + "|-|" + heartid)
                r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
    #            r.zincrby("bmk:doc:share:byfllw",heartusr+"|-|"+heartid,-1)
            elif heartopt == "add":
                r.sadd(fllwkey, username)
#                 r.sadd("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)
                r.zadd("usr:" + username + ":fllw" , time.time(), heartusr + "|-|" + heartid)
                r.zadd("bmk:doc:share:byfllw", r.scard(fllwkey), heartusr + "|-|" + heartid)
            
#     if orderby=="tms":
#         sharebeacons = r.zrevrange("bmk:doc:share",0,-1)
#     elif orderby=="fllw":
#         sharebeacons = r.zrevrange("bmk:doc:share:byfllw",0,-1)
#     elif orderby=="news":
#         sharebeacons = r.zrevrange("bmk:doc:share:bynews",0,-1)
    sharebeacons = r.zrevrange("bmk:doc:share", 0, -1) 
#     mybeacons = r.smembers("usr:" + username+":fllw") 
    mybeacons = r.zrevrange("usr:" + username + ":fllw", 0, -1)
    
    for beaconstr in mybeacons:
        beausr, beaid = beaconstr.split("|-|") 
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = r.scard("bmk:" + beausr + ":" + beaid + ":fllw")
        beaobj["id"] = beaid
        beaobj["new_cnt"] = getBeaconNewsCnt(username, beausr, beaid)
        if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
            continue
        myfllw_list.append(beaobj)
    
    sharebeacons = listsub(sharebeacons, mybeacons) 
    for beaconstr in sharebeacons:
        beausr, beaid = beaconstr.split("|-|")
#        print "bmk:" + beausr + ":" + beaid +"==="+str(r.scard("bmk:" + beausr + ":" + beaid+":fllw"))
        beaobj = r.hgetall("bmk:" + beausr + ":" + beaid) 
        beaobj["fllw_cnt"] = r.scard("bmk:" + beausr + ":" + beaid + ":fllw")
        beaobj["new_cnt"] = getBeaconNewsCnt(username, beausr, beaid)
        beaobj["id"] = beaid
        if not beaobj.has_key("ttl"):  # 如果该灯塔已经被删除了(脏数据)
            continue
        sharebeacon_list.append(beaobj)
          
        if not beaconname == "":  # 根据beaconid取所有同名的灯塔(如果是查询)
            if beaobj.has_key("name"):
                beaconttl = beaobj["name"]
            else:
                continue
            beaconname = to_unicode_or_bust(beaconname)
            beaconttl = to_unicode_or_bust(beaconttl, "utf8") 
            if re.search(beaconname, beaconttl):
                beacon_search.append(beaobj) 
                
    if beaconid != "":
        try:
            udata = buildBeaconData(beaconusr, beaconid, start=0 , end=300,orderby=orderby) 
        except:
            logger.error("buildBeaconData(%s,%s) is error====" %(beaconusr, beaconid))
            traceback.print_exc()
        beaconname = r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl") 
        beacondisname = r.hget("bmk:" + beaconusr + ":" + beaconid, "name") 
        r.hset("usr:" + username + ":channeltms", beaconusr + ":" + beaconid, time.time())  # 增加用户关于该频道的最后跟新时间
        cnt = len(udata["docs"]) if udata.has_key("docs") else 0
        r.hset("bmk:" + beaconusr + ":" + beaconid, "cnt", cnt)
    else:  
        udata = getAllBeaconDocsByUser(username, newscnt=5)
#         udata["simdocs"]=udata.pop("docs") 
        
    return render_to_response(template_name, {
        'udata': udata,
        'mybeacons':mybeacon_list,
        'myfllw_list':myfllw_list,
        'sharebeacons':sharebeacon_list,
        'beaconid':beaconid,  # 当前灯塔的ID
        'beaconusr':beaconusr,  # 当前灯塔的ID
        'beaconname':beaconname,  # 当前灯塔的名称
        'beacondisname':beacondisname,  # 当前灯塔的名称
        'beacon_search':beacon_search,
        "greetings":getGreeting(),
        'orderby':orderby,
        'isadmin':isadmin,
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
    if username not in ["ltb", "wxi", "sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    beacon_json = {}
    beacon_list = []
    
    udata = {}
    beacondesc = ""
    beaconname = "" 
    beacontime = ""
    beacontag = ""
    beacondisplayname = ""
    beaconmindoc = 0
    headlineonly = "0"
    if beaconid != "":  
        udata = buildBeaconData(beaconusr, beaconid)
        beacondesc = r.hget("bmk:" + beaconusr + ":" + beaconid, "desc") 
        beaconname = r.hget("bmk:" + beaconusr + ":" + beaconid, "ttl") 
        beacontime = r.hget("bmk:" + beaconusr + ":" + beaconid, "crt_tms")
        beacontime = getTime(beacontime, formatstr="%Y-%m-%d-%H:%M:%S", addtimezone=False)
        beacondisplayname = r.hget("bmk:" + beaconusr + ":" + beaconid, "name")
        beacontag = r.hget("bmk:" + beaconusr + ":" + beaconid, "tag")
        beaconmindoc = r.hget("bmk:" + beaconusr + ":" + beaconid, "mindoc") 
        beaconmindoc = 0 if beaconmindoc is None else beaconmindoc
        headlineonly = r.hget("bmk:" + beaconusr + ":" + beaconid, "headlineonly") 
        headlineonly = "0" if headlineonly is None else headlineonly
#         shared = False if r.zrank("bmk:doc:share", beaconusr + "|-|" + beaconid) is None else True
#         r.hset("bmk:" + beaconusr + ":" + beaconid,"cnt",len(udata["docs"]))

#     beacons = r.smembers("bmk:" + username)
    beacons = r.zrevrange("bmk:doc:share", 0 , -1)
#     print beacons
    for beaconstr in beacons:
        busr, bid = beaconstr.split("|-|")
        beaobj = r.hgetall("bmk:" + busr + ":" + bid) 
        beaobj["id"] = bid
        beaobj["crt_usr"] = busr
#         beaobj["shared"] = False if r.zrank("bmk:doc:share", beaconusr + "|-|" + beaconid) is None else True
        beacon_list.append(beaobj)   
    if beacontime == "":
        beacontime = getTime(time.time(), formatstr="%Y-%m-%d-%H:%M:%S", addtimezone=False)
    return render_to_response(template_name, {
        'current_path': request.get_full_path(),
        'udata': udata,
        'beacons':beacon_list,
        'beaconid':beaconid,  # 当前灯塔的ID
        'beacontime':beacontime,  # 当前灯塔的ID
        'beacondesc':beacondesc,  # 当前灯塔的备注
        'beacontag':beacontag,  # 当前灯塔的备注
        'beaconname':beaconname,  # 当前灯塔的名称 
        'beacondisplayname':beacondisplayname,  # 当前灯塔的名称
        'beaconusr':beaconusr,  # 当前灯塔的名称  
        'beaconmindoc':beaconmindoc,
        'headlineonly':headlineonly,
        "user": userobj,
    }, context_instance=RequestContext(request)) 

@login_required
def beacondelete(request, template_name="beacon/beacon_list.html"):  
    username = getUserName(request)  
    if username not in ["ltb", "wxi", "sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    beaconusr = request.GET.get("beaconusr", "")
    beaconid = request.GET.get("beaconid", "")
#     print beaconusr,beaconid
    key = "bmk:" + beaconusr + ":" + beaconid
    channel = r.hget(key, "ttl")
    quantity = log_typer(request, "beacondelete", to_unicode_or_bust(channel))
    r.zrem("bmk:doc:share", beaconusr + "|-|" + beaconid) 
    r.zrem("bmk:doc:share:byfllw", beaconusr + "|-|" + beaconid) 
    r.zrem("bmk:doc:share:bynews", beaconusr + "|-|" + beaconid)
    r.zrem("usr:" + beaconusr + ":fllw", beaconusr + "|-|" + beaconid)
    key = "bmk:" + beaconusr + ":" + beaconid
    for usr in r.smembers(key + ":fllw"):
        r.zrem("usr:" + usr + ":fllw", beaconusr + "|-|" + beaconid)
    r.delete(key + ":doc:tms")
    r.delete(key + ":fllw")
    r.delete(key)
    
    r.delete("channel:" + beaconusr + ":" + beaconid + ":doc_dcnt")
    r.delete("channel:" + beaconusr + ":" + beaconid + ":doc_tcnt")
    
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
    query = query.replace(" ", "")
    userobj = request.user
    if userobj.is_anonymous():  # 用户未登录
        return HttpResponse('<h1>只有登录用户才能访问该功能..</h1>')
    username = getUserName(request)
    
    if username not in ["wxi", "sj", "ltb"]:  #
        return HttpResponse('<h1>只有管理用户才能访问该功能..</h1>')
#    user_list = r.keys("usr:*:ppl:uptms")
    usrlst = []
    if otype == "log":
        userinfos = r.zrevrange("log", 0, 1000)
        for userinfo in userinfos:
#            print userinfo
            usr = json.loads(userinfo)  
#             usr["act_tms"] = getTime(usr["tms"])
#             usr["act_tms"] = usr["act_tms"][0:19]
#            if usr["ip"] not in ["203.208.60.217","203.208.60.218","203.208.60.219","123.125.71.38"]:
            if query == "" :
                usrlst.append(usr)
            elif usr["ip"] == query or usr["usr"] == query:
                usrlst.append(usr)
    else:
        userinfos = r.hgetall("usrlst")
#        print userinfos
        for user, userinfo in userinfos.items():
            usr = json.loads(userinfo)  
#             usr["act_tms"] = getTime(usr["tms"])
            usrlst.append(usr)
        usrlst = sorted(usrlst, key=lambda l:l["act_tms"], reverse=True)
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
    if username not in ["wxi", "sj", "ltb"]:  #
        return HttpResponse('<h1>只有管理用户才能访问该功能..</h1>')
    hourbefore = request.GET.get("hourbefore", "8")
    beaconid = request.GET.get("beacon", "allbeacons")
    user = request.GET.get("u", username) 
    pushQueue("sendemail", user, "bybeacon", tag=hourbefore, similarid=beaconid)
    return HttpResponse("sendemail is okay.") 
    
@login_required
def sendemailfornews(request):
    print "===sendemailfornews==="
    
    username = getUserName(request)  
    usr_email = r.hget("usr:" + username, "email")
    groupname = request.GET.get("group", "all")
    groupemail = ",".join(r.zrevrange("usr:" + username + ":buddy:" + groupname, 0, -1))
    emails = request.GET.get("emails", "")
    docids = request.GET.get("docids", "")
    otype = request.GET.get("o", "") 
    
    robj = {}
    if emails == "":
        robj["message"] = "email must be not null !"
        robj["success"] = "failed"
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    
    quantity = log_typer(request, "sendemailfornews", emails + "->" + docids)
#     if quantity > getsysparm("QUANTITY"):
#         return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    def pushemail(emails, docids):
        for email, docid in zip(emails.split(","), docids.split(";")):
#             pushQueue("sendemail", username, "byemail", tag=email, similarid=docid)
            pushQueue("sendemail",{"emailtype":"bydocid","email":email,"docid":docid})
            
    if otype == "service":
        if emails != "":
#             pushQueue("sendemail", username, "byemail", tag=emails, similarid=docids.replace(",",";"))
            pushemail(emails, docids.replace(",", ";"))
            robj["message"] = "send email to:" + emails 
        else:
#             pushQueue("sendemail", username, "byemail", tag=usr_email, similarid=docids.replace(",",";"))
            pushemail(usr_email, docids.replace(",", ";"))   
            robj["message"] = "send email to:" + usr_email
        if groupname != "": 
            robj["group"] = groupname
        robj["success"] = 'true'
        robj["docid"] = docids
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    
    if emails != "":
        sendemailbydocid(emails, docids)
    else: 
        sendemailbydocid(usr_email, docids)
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
    if quantity > getsysparm("QUANTITY"):
        return HttpResponse('<h1>亲,你今天访问次数太多了..请休息一会再来</h1>')
    if captchaid != "":
        r.hset("captcha:" + captchaid, "issendmail", True)
        username = r.hget("captcha:" + captchaid, "crt_usr")
        usr_email = r.hget("usr:" + username, "email")
        url = "http://" + request.META['HTTP_HOST'] + "/apply/?captcha=" + captchaid 
#        content=username+""",您好!\r\n欢迎您的注册,在访问过程中有任何疑问及建议可以给我们邮件或者在网站中提交建议,\r\n
#        现在,您可以邀请您的朋友们通过以下链接来指极星注册:\r\n  """.decode("utf8")+url
        content = username + ",这是来自指极星的邀请，欢迎！\r\n\r\n指极星，帮助您在浩瀚空间中发现您关注的资讯。\r\n\r\n邀请码：".decode("utf8") + captchaid
        content += "\r\n\r\n点击加入".decode("utf8") + url + " ，主观、客观、达观的共同探索。".decode("utf8")
        sendemail(content, usr_email)
        return HttpResponseRedirect("/news/captchalist/")
#    print request
    captchas = r.keys("captcha:*")
    captchaobjs = []
    cdata = {}
    for cap in captchas:
        cdata = r.hgetall(cap)
        tms = cdata["crt_tms"] if cdata.has_key("crt_tms") else "0"
        cdata["id"] = cap.replace("captcha:", "")
        cdata["crt_tms"] = getTime(tms)
        cdata["tms"] = tms
        captchaobjs.append(cdata)
    captchaobjs = sorted(captchaobjs, key=lambda l:l["tms"], reverse=True)
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
