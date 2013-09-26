#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
import json,re
import csv, string
import sys, time
import redis
#from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.contrib import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils.encoding import smart_str
from mybonds.apps.geeknews import * 

# def staticpage11(request, page_name):
#    # Use some exception handling, just to be safe
#    print page_name +"===" 
#    print ('%s/.htm' % (page_name, ))
#    try:
#        return direct_to_template(request, '%s/.htm' % (page_name, ))
#    except TemplateDoesNotExist:
#        raise Http404 

# r = redis.StrictRedis(host=REDIS_HOST, port=6380, db=0)
def staticpage(request, page_name):
    # return HttpResponse("You're voting on poll %s." % poll_id)
    head_list = ['Duration', 'CURRENT YLD', 'PREV YLD', 'CHANGE', '1 WK YLD', '1 MO YLD', '6 MO YLD'];
    t = loader.get_template('examples/line-basic//index.html')
    c = Context({
        'head_list': head_list,
    })
    return HttpResponse(t.render(c))

def get_captcha(request):
    return HttpResponse("9527")

def apply_service(request):
    username = request.GET.get("usr", "");
    username = username.lower()
    password = request.GET.get("pwd", "");
    email = request.GET.get("email", "");
    captcha = request.GET.get("captcha", "");
    api = request.GET.get("api", "")
    robj = {}
    robj["api"]=api
    if username == "" or password == "" or email == "" or captcha == "":
        robj["success"] = 'false'
        robj["message"] = "username or password or email or captcha is null"
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
#    if r.exists("usr:" + username):
    if username_present(username):
        robj["success"] = 'false'
        robj["message"] = "user %s exists already" % (username)
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    if r.hget("captcha:"+captcha,"used_usr")!="":
        robj["success"] = 'false'
        robj["message"] = "captcha %s is error or used already " % (username)
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        robj["success"] = 'false'
        robj["message"] = "email %s is error" % (email)
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
        
    
    User.objects.create_user(username=username, email=email , password=password)
    r.hset("usr:" + username, "nm", username)
    r.hset("usr:" + username, "email", email) 
    r.hset("usr:" + username, "crt_tms", time.time()) 
    r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
    r.hset("usr:" + username, "fllw_bmk_cnt", 0) 

    if captcha=="111111":#测试用的验证码
        r.hset("captcha:"+captcha,"used_usr","") 
        
    def saveCaptcha(captcha):
        r.hset("captcha:"+captcha,"crt_usr",username)
        r.hset("captcha:"+captcha,"crt_tms",time.time())
        r.hset("captcha:"+captcha,"used_usr","")
        r.hset("captcha:"+captcha,"used_tms","")
        r.hset("captcha:"+captcha,"issendmail",False)
    saveCaptcha(id_generator())
#     saveCaptcha(id_generator())
#     saveCaptcha(id_generator())
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        robj["success"] = 'true'
        robj["message"] = "apply is success" 
        robj["data"] = r.hgetall("usr:" + username)
        greeting_typer(username, "apply", username)

        fllwkey="bmk:rd:1108470809:fllw"
        if r.exists(fllwkey):
            r.sadd(fllwkey,username) 
            r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|1108470809")
            r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|1108470809")
        
        fllwkey="bmk:rd:954189947:fllw"
        if r.exists(fllwkey):
            r.sadd(fllwkey,username) 
            r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|954189947")
            r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|954189947")
    else:
        robj["success"] = 'false'
        robj["message"] = "disabled account!" 
        robj["data"] = []
    robj["api"]=api
    return HttpResponse(json.dumps(robj), mimetype="application/json")

@csrf_protect
def apply(request):
    """
    Create a login for a new customer.  
    """
    err_message = "请使用英文字母或数字注册,\r\n 并输入正确的邮箱地址".decode("utf8")
#    #return HttpResponse("You're voting on poll %s." % poll_id)
#    print request
    if  request.method == 'GET':
        captcha = request.GET.get("captcha", "111111") 
        t = loader.get_template('apply.html')
        c = Context({
            'captcha': captcha,
            'err_message': err_message,
        })
        return render_to_response('apply.html',
                                  {'captcha': captcha,
                                    'err_message': err_message,
                                   },
                                  context_instance=RequestContext(request))
    
    if  request.method == 'POST':
        username = request.POST.get("username", "");
        username = username.lower()
        password = request.POST.get("password", "");
        email = request.POST.get("email", "yxxiwang@gmail.com");
        captcha = request.POST.get("captcha", "111111");
        if username == "" or password == "" or email == "" or captcha == "" or len(username)>20: 
            return render_to_response('apply.html',
                                      {'err_message': err_message,
                                        'username': username, 
                                      },
                                      context_instance=RequestContext(request))
#        print "========"
#        print r.hget("captcha:"+captcha,"used_usr")
#        print "========"
        used_usr = r.hget("captcha:"+captcha,"used_usr") 
        used_usr = used_usr if used_usr is not None else ""
        if len(used_usr)>0:
            return render_to_response('apply.html',
                                      {'err_message': "邀请码错误或者已被使用",
                                        'username': username, 
                                        'email': email,
                                        'captcha': captcha,
                                      },
                                      context_instance=RequestContext(request))
            
        if not isAscii(username): 
            return render_to_response('apply.html',
                                      {'err_message': err_message,
                                        'username': username,
                                        'captcha': captcha,
                                       },
                                      context_instance=RequestContext(request))
        try:
#            if User.objects.get(username__exact=username):
#                return render_to_response('apply.html', 
#                                          {'err_message': "用户已存在!".decode("utf8")},
#                                          context_instance=RequestContext(request))
#            if r.exists("usr:" + username):
            if username_present(username):
                return render_to_response('apply.html',
                                          {'err_message': username + " 该名称已被抢注,考虑换一个用户名吧".decode("utf8"),
                                           'username': username + str(random.randint(100, 999)),
                                           'captcha': captcha,
                                           },
                                          context_instance=RequestContext(request))
            User.objects.create_user(username=username, email=email , password=password)
            r.hset("usr:" + username, "nm", username)
            r.hset("usr:" + username, "name", username)
            r.hset("usr:" + username, "email", email) 
            r.hset("usr:" + username, "crt_tms", time.time())
            r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
            r.hset("usr:" + username, "fllw_bmk_cnt", 0)
            
            r.hset("captcha:"+captcha,"used_usr",username) 
            r.hset("captcha:"+captcha,"used_tms",time.time()) 
            
            if captcha=="111111":#测试用的验证码
                r.hset("captcha:"+captcha,"used_usr","") 
                
            def saveCaptcha(captcha):
                r.hset("captcha:"+captcha,"crt_usr",username)
                r.hset("captcha:"+captcha,"crt_tms",time.time())
                r.hset("captcha:"+captcha,"used_usr","")
                r.hset("captcha:"+captcha,"used_tms","")
                r.hset("captcha:"+captcha,"issendmail",False)
            saveCaptcha(id_generator())
#             saveCaptcha(id_generator())
#             saveCaptcha(id_generator())
            
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                log_typer(request, "apply", "none")
                greeting_typer(username, "apply", username)

                fllwkey="bmk:rd:1108470809:fllw"
                if r.exists(fllwkey):
                    r.sadd(fllwkey,username) 
                    r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|1108470809")
                    r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|1108470809")
                
                fllwkey="bmk:rd:954189947:fllw"
                if r.exists(fllwkey):
                    r.sadd(fllwkey,username) 
                    r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|954189947")
                    r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|954189947")
#                 print user.is_authenticated()
#                 urlstr="http://%s/news/sfllowbeacon/?u=%s&fllwopt=add&beaconid=1108470809&beaconusr=rd" %(getsysparm("DOMAIN"),username)
#                 loadFromUrl(urlstr)
#                 urlstr="http://%s/news/sfllowbeacon/?u=%s&fllwopt=add&beaconid=954189947&beaconusr=rd" %(getsysparm("DOMAIN"),username)
#                 loadFromUrl(urlstr)
                return HttpResponseRedirect('/news/beaconnews')
            else:
                # Return a 'disabled account' error message 
                return render_to_response('apply.html',
                                      {'err_message': 'disabled account!'}, context_instance=RequestContext(request))
        except "user.DoesNotExist": 
            print "apply user failed"
            return render_to_response('apply.html', context_instance=RequestContext(request))
        return render_to_response('apply.html', context_instance=RequestContext(request))

@login_required
def buddyhold(request):
    optype = request.GET.get("o", "service")
    acttype = request.GET.get("a", "list")
    groupname = request.GET.get("group", "all")
    username = getUserName(request)
#    username = request.GET.get("u", getUserName(request))
    api = request.GET.get("api", "")
    robj = {}
    robj["api"]=api
    if optype =="service":
        if acttype == "list":
            emails = r.zrevrange("usr:"+username+":buddy:"+groupname,0 ,-1)
            email_list=[]
            for email in emails:
                emailobj={}
                emailobj["email"]=email
                email_list.append(emailobj)
            robj["emails"] = email_list
            robj["group"] = groupname
            robj["success"] = 'true'
            robj["message"] = "list email is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        elif acttype == "add":
            emailstr = request.GET.get("email", "")
            emails = emailstr.split(",")
            email_list=[]
            for email in emails:
                emailobj={}
                r.zadd("usr:"+username+":buddy:"+groupname,time.time(),email) 
                emailobj["email"]=email
                email_list.append(emailobj)
            robj["emails"] = email_list
            robj["group"] = groupname
            robj["success"] = 'true'
            robj["message"] = "add email is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        elif acttype == "delete":
            emailstr = request.GET.get("email", "")
            emails = emailstr.split(",")
            email_list=[]
            for email in emails:
                emailobj={}
                r.zrem("usr:"+username+":buddy:"+groupname,email) 
                emailobj["email"]=email
                email_list.append(emailobj)
            robj["emails"] = email_list
            robj["group"] = groupname
            robj["success"] = 'true'
            robj["message"] = "delete email is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        elif acctype == "relative":
#            groupids = groupname.split(",")
            groups = r.zrevrange("usr:"+username+":group:lst",0,-1)
            group_list=[]
#            for groupid in groups:
#                if r.zscore("usr:"+username+":buddy:"+groupid,email) is None:
        else:
            robj["success"] = 'false'
            robj["message"] = "unknow action type."
            return HttpResponse(json.dumps(robj), mimetype="application/json")
            
    else:
        return HttpResponse("ok")
        

def test(request, template_name="beacon/test.html"): 
#     tempparmsobj = r.hgetall("tempparms")
    bkcolor = r.hget("tempparms","bkcolor")
    fontsize = r.hget("tempparms","fontsize")
    padding = r.hget("tempparms","padding")
    fontcolor = r.hget("tempparms","fontcolor")
    fontfamily = r.hget("tempparms","fontfamily") 
#     padding = request.GET.get("padding", "0px 9px 0px 9px") 
#     fontcolor = request.GET.get("fontcolor", "red") 
#     fontfamily = request.GET.get("fontfamily", """"Arial Hebrew","Microsoft Yahei";""")
#     font = request.GET.get("font", "18.5px/1.8 Arial,\5FAE\8F6F\96C5\9ED1,\82F9\679C\4E3D\4E2D\9ED1;")
    print fontsize,padding,bkcolor
    return render_to_response(template_name, { 
        'bkcolor': bkcolor, 
        'fontsize': fontsize,
        'padding':padding,
        'fontcolor':fontcolor,
        'fontfamily':fontfamily,
#         'font':font,
    }, context_instance=RequestContext(request))  

@login_required
def groupdelete(request, template_name="beacon/group_list.html"): 
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    groupid = request.GET.get("groupid", "")
    r.zrem("groups",groupid)
    r.delete("group:"+groupid)
    return HttpResponseRedirect("/grouplist/")
    
@login_required
def groupsave(request, template_name="beacon/group_list.html"): 
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    gname = request.GET.get("gname", "")
    gdesc = request.GET.get("gdesc", "")
    gid = getHashid(gname)
    r.hset("group:"+gid,"name",gname)
    r.hset("group:"+gid,"desc",gdesc)
    r.zadd("groups",time.time(),gid)
    
    return HttpResponseRedirect("/grouplist/?groupid="+gid)
    
@login_required
def grouplist(request, template_name="beacon/group_list.html"):
    groupid = request.GET.get("groupid", "")
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    beacons = []
    gobj ={}
    if groupid != "":  
        gobj = r.hgetall("group:"+groupid)
#         gname = "" if gname is None else gname
        for bstr in r.zrevrange("bmk:doc:share",0,-1):
#             busr,bid = bstr.split("|-|")
            key = "bmk:"+bstr.replace("|-|",":")
            bttl = r.hget(key,"tag")
            bttl = "" if bttl is None else bttl
#             if re.search(gobj["name"],bttl):
            if gobj["name"] in bttl.split(","):
                beacons.append(r.hgetall(key))
        
    groups = [] 
    g_lst = r.zrevrange("groups", 0,-1)  # 组集合
    for gid in g_lst:
        group = r.hgetall("group:"+gid)
        group["id"]=gid
        groups.append(group)
        
#     print beacons
    return render_to_response(template_name, { 
        'gobj': gobj,
        'groupid': groupid,
        'groups': groups,
        'beacons':beacons,
    }, context_instance=RequestContext(request)) 

# @login_required
# def groupmanage(request):
#     optype = request.GET.get("o", "")
#     acttype = request.GET.get("a", "list")
#     username = getUserName(request)
#     robj={}
#     if optype =="service":
#         if acttype == "list":
#             email = request.GET.get("email", "")
#             groups = r.zrevrange("usr:"+username+":group:lst",0,-1)
#             group_list=[]
#             for groupid in groups:
#                 groupobj=r.hgetall("usr:"+username+":group:"+groupid)
#                 groupobj["groupid"]=groupid
#                 if not email=="":
#                     if r.zscore("usr:"+username+":buddy:"+groupid,email) is None:
#                         groupobj["hasemail"]="0" 
#                     else:
#                         groupobj["hasemail"]="1"  
#                 else:
#                     groupobj["hasemail"]=str(r.zcard("usr:"+username+":buddy:"+groupid))
#                 group_list.append(groupobj)
# #            group_list.append({"groupid":"all","groupname":"all"})
#             robj["groups"] = group_list
#             robj["success"] = 'true'
#             robj["message"] = "list group is success"
#             return HttpResponse(json.dumps(robj), mimetype="application/json")
#         elif acttype == "add": 
#             groupname = request.GET.get("groupname", "")
#             if groupname !="":
#                 groupid = getHashid(groupname)
#                 r.zadd("usr:"+username+":group:lst",time.time(),groupid)
#                 r.hset("usr:"+username+":group:"+groupid,"groupname",groupname)  
#                 robj["groupid"]=groupid 
#             robj["groupname"]=groupname  
#             robj["groupid"]=groupid  
#             robj["success"] = 'true'
#             robj["message"] = "add group is success"
#             return HttpResponse(json.dumps(robj), mimetype="application/json")
#         elif acttype == "delete":
#             groupid = request.GET.get("groupid", "")
#             groupname=""
#             if groupid !="":
#                 groupname=r.hget("usr:"+username+":group:"+groupid,"groupname")
#                 r.zrem("usr:"+username+":group:lst",groupid)
#                 r.delete("usr:"+username+":group:"+groupid)
#                 r.delete("usr:"+username+":buddy:"+groupid)
#             robj["groupid"]=groupid
#             robj["groupname"]=groupname
#             robj["success"] = 'true'
#             robj["message"] = "delete group is success"
#             return HttpResponse(json.dumps(robj), mimetype="application/json")
#             
#     else:
#         return HttpResponse("ok")
        
@login_required
def queuelist(request,template_name="beacon/queue_list.html"):
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    delete = request.GET.get("delete", "")
    if delete == "beacon":
        r.delete("queue:beacon")
    elif  delete == "removedoc":
        r.delete("queue:removedoc")
    elif  delete == "sendemail":
        r.delete("queue:sendemail")
    
    def loadbeacon(obj,type='beacon'):
        if type == "beacon":
            bobj = json.loads(obj) 
    #         bobj["tms"] = bobj["tms"][0:19] 
            bkey = "bmk:"+bobj["beaconusr"]+":"+bobj["beaconid"]
            bobj["name"] = r.hget(bkey,"name").decode("utf8") +" --> days:"+bobj["days"] if r.hget(bkey,"name") is not None else "None"
        elif type=="remove": 
            bobj = json.loads(obj) 
#             bobj["name"] = r.hget("bmk:"+bobj["beacon"],"name")
            bobj["name"] = bobj["channel"]
        return bobj
    beaconqueue_list = r.lrange("queue:beacon:processing",0,-1) + r.lrange("queue:beacon",0,20)
    bqcnt= r.llen("queue:beacon")
    bqcnt = bqcnt+1 if bqcnt!=0 else 0#将正在处理的记录加上
    bqcntdone= r.llen("queue:beacon:done")
    beaconqueue_done_list = r.lrange("queue:beacon:done",0,5)
    beaconqueue_list = [loadbeacon(obj) for obj in beaconqueue_list]
    beaconqueue_done_list = [loadbeacon(obj) for obj in beaconqueue_done_list]
    
    removeq_list = r.lrange("queue:removedoc:processing",0,-1) + r.lrange("queue:removedoc",0,20)
    rqcntdone= r.llen("queue:removedoc:done")
    rqcnt= r.llen("queue:removedoc")
    rqcnt = rqcnt+1 if rqcnt!=0 else 0
    removeq_done_list = r.lrange("queue:removedoc:done",0,5)
    removeq_list = [loadbeacon(obj,"remove")  for obj in removeq_list]
    removeq_done_list = [loadbeacon(obj,"remove")  for obj in removeq_done_list]
    
    sendemail_list = r.lrange("queue:sendemail:processing",0,-1) + r.lrange("queue:sendemail",0,20)
    sqcntdone= r.llen("queue:sendemail:done")
    sqcnt= r.llen("queue:sendemail")
    sqcnt = sqcnt+1 if sqcnt!=0 else 0
    sendemail_done_list = r.lrange("queue:sendemail:done",0,5)
    sendemail_list = [json.loads(obj)  for obj in sendemail_list]
    sendemail_done_list = [json.loads(obj)  for obj in sendemail_done_list]
    
    return render_to_response(template_name, { 
        'username':username, 
        'beaconqueues':beaconqueue_list,
        'beaconqueuedones':beaconqueue_done_list,
        'bqcnt':bqcnt,
        'bqcntdone':bqcntdone,
        
        'removeqs':removeq_list,
        'removeqdones':removeq_done_list,
        'rqcnt':rqcnt,
        'rqcntdone':rqcntdone,
        
        'sendemailqs':sendemail_list,
        'sendemailqdones':sendemail_done_list,
        'sqcnt':sqcnt,
        'sqcntdone':sqcntdone,
        'current_path': request.get_full_path(),
    }, context_instance=RequestContext(request)) 

    
@login_required
def sysparms(request,template_name="beacon/sysparms.html"):
    username = getUserName(request)
    if username not in ["ltb","wxi","sj"] :  
        return HttpResponse('<h1>只有超级用户才能访问该功能..</h1>')
    if  request.method == 'GET':
        sysparmsobj = r.hgetall("sysparms")
        tempparmsobj = r.hgetall("tempparms")
         
        return render_to_response(template_name, { 
            'username':username, 
            'tempparmsobj':tempparmsobj,
            'sysparmsobj':sysparmsobj,
            'current_path': request.get_full_path(),
        }, context_instance=RequestContext(request)) 
    
    if  request.method == 'POST': 
        parmtype = request.POST.get("parmtype", "system");
        print parmtype 
        if parmtype == "system":
            redis_expire = request.POST.get("redis_expire", "186400");
            backend_domain = request.POST.get("backend_domain", "svc.zhijixing.com");
            domain = request.POST.get("domain", "www.9cloudx.com");
            doc_expire = request.POST.get("doc_expire","172800");
            beacon_interval =request.POST.get("beacon_interval", "900"); 
            beacon_news_num =request.POST.get("beacon_news_num", "300");
            quantity = request.POST.get("quantity", "1500");
            quantity_duration = request.POST.get("quantity_duration", "300"); 
            loglevel = request.POST.get("loglevel", "info"); 
            failed_retry_times = request.POST.get("failed_retry_times", "3");  
            r.hset("sysparms","redis_expire",int(redis_expire))
            r.hset("sysparms","backend_domain",backend_domain)
            r.hset("sysparms","domain",domain)
            r.hset("sysparms","doc_expire",int(doc_expire))
            r.hset("sysparms","beacon_interval",int(beacon_interval)) 
            r.hset("sysparms","beacon_news_num",int(beacon_news_num))
            r.hset("sysparms","quantity",int(quantity))
            r.hset("sysparms","quantity_duration",int(quantity_duration))
            r.hset("sysparms","failed_retry_times",int(failed_retry_times))
            r.hset("sysparms","loglevel",loglevel)
        elif parmtype == "template":
            fontsize = request.POST.get("fontsize", "50px");
            fontcolor = request.POST.get("fontcolor", "blue");
            fontfamily = request.POST.get("fontfamily", """ "Arial Hebrew","Microsoft Yahei" """);
            bkcolor = request.POST.get("bkcolor", "#f5f5f5");
            padding = request.POST.get("padding", "0px 9px 6px 9px");
            r.hset("tempparms","fontsize",fontsize)
            r.hset("tempparms","fontcolor",fontcolor)
            r.hset("tempparms","fontfamily",fontfamily)
            r.hset("tempparms","bkcolor",bkcolor)
            r.hset("tempparms","padding",padding)
             
        sysparmsobj = r.hgetall("sysparms") 
        tempparmsobj = r.hgetall("tempparms")
        return render_to_response(template_name, {
            'err_message': "用户信息保存成功".decode("utf8"),
            'username':username, 
            'sysparmsobj':sysparmsobj,
            'tempparmsobj':tempparmsobj,
            'current_path': request.get_full_path(),
        }, context_instance=RequestContext(request)) 
        
@login_required
def user_delete(request): 
    username = getUserName(request)
    if username not in ["wxi","sj","ltb"]:#
        return HttpResponse('<h1>只有管理用户才能访问该功能..</h1>')
    delusr = request.GET.get("username", "");
    try:
        user = User.objects.get(username=delusr)
    except:
        r.hdel("usrlst",delusr)
        r.delete("usr:"+delusr+":channeltms")
        r.delete("usr:"+delusr)
    else:
        if user is not None and user.is_active:
            user.delete()
            r.hdel("usrlst",delusr)
            r.delete("usr:"+delusr)
            r.delete("usr:"+delusr+":fllw")
            r.delete("usr:"+delusr+":channeltms")
            r.delete("usr:"+delusr+":buddy:all")
        return HttpResponse('user %s is deleted' % delusr)
        
@login_required
def user_modify(request,template_name="beacon/usermodify.html"): 
    optype = request.GET.get("o", "");
#    username = request.GET.get("u", "");
    username = getUserName(request)
    password = request.GET.get("pwd", "");
    newpwd = request.GET.get("newpwd", "");
    displayname = request.GET.get("displayname", "");
    email = request.GET.get("email", "");
    rssuser = request.GET.get("rssuser", "");
    api = request.GET.get("api", "")
    robj={}
    robj["api"]=api
    if  request.method == 'GET':
        if optype =="service":
            if newpwd !="": 
                user = auth.authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    user = User.objects.get(username=username)
                    user.set_password(newpwd)
                    user.save()
                else:
        #            user = User.objects.get(username=username)
        #            user.set_password(newpwd)
        #            user.save()
                    robj["success"] = 'failed'
                    robj["message"] = "login failed" 
                    return HttpResponse(json.dumps(robj), mimetype="application/json")
            if displayname !="":
                r.hset("usr:" + username, "displayname", smart_str(displayname))
            if email !="":
                r.hset("usr:" + username, "email", email) 
            if rssuser !="":
                if rssuser=="1" or rssuser==str.lower("true"):
                    r.sadd("rssuser",username)
                else:
                    r.srem("rssuser",username)
            robj = r.hgetall("usr:" + username)
            robj["rssuser"]= "1" if r.sismember("rssuser",username) else "0"
            robj["success"] = 'true'
            robj["message"] = "user modify is success"
            robj["api"]=api
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        else:
            email = r.hget("usr:"+username,"email")
            name = r.hget("usr:"+username,"name")
            displayname = smart_str(r.hget("usr:"+username,"displayname"))
                
            return render_to_response(template_name, {
                'username':username,
                'displayname':displayname,
                'email':email,
                'current_path': request.get_full_path(),
            }, context_instance=RequestContext(request))
    if  request.method == 'POST':
        quantity = log_typer(request, "user_modify", username)
        
        displayname = request.POST.get("displayname", "");
        password = request.POST.get("password", "");
        email = request.POST.get("email", "");
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return render_to_response(template_name, {
                'err_message': "邮箱格式有误.".decode("utf8"),
                'username':username,
                'displayname':displayname,
                'email':email,
                'current_path': request.get_full_path(),
            }, context_instance=RequestContext(request)) 
        if email !="":
            r.hset("usr:"+username,"email",email)
        if displayname !="":
            r.hset("usr:"+username,"displayname",displayname)
        if password !="":
            user = User.objects.get(username=username)
            if user is None:
                return render_to_response(template_name, {'err_message': "无此用户,是否邮箱未注册?".decode("utf8")}, context_instance=RequestContext(request))
            user.set_password(password)
            user.save()
#         print username,displayname,email
        return render_to_response(template_name, {
            'err_message': "用户信息保存成功".decode("utf8"),
            'username':username,
            'displayname':displayname,
            'email':email,
            'current_path': request.get_full_path(),
        }, context_instance=RequestContext(request)) 
        
def character(request, template_name="beacon/suggestion.html"): 
    otype = request.GET.get("o", "")
    charts = r.smembers("character")
    chart_list = []
    chartobj ={}
    if otype =="service":
        robj={}
        robj["total"] = str(len(charts))
        robj["message"] = "success"
        for chart in charts:
            chartobj = r.hgetall("usr:"+chart)
            chart_list.append(chartobj)
        robj["data"] = chart_list
    return HttpResponse(json.dumps(robj), mimetype="application/json")
        
    return render_to_response(template_name, {
        'current_path': request.get_full_path(),
        'charts': charts, 
        "user": userobj,
    }, context_instance=RequestContext(request))
    
def login_apply(request):
    username = request.GET.get("usr", "");
    username = username.lower()
    password = request.GET.get("pwd", "");
    api = request.GET.get("api", "")
    robj = {}
    robj["api"]=api
    if username == "" or password == "":
        robj["success"] = 'false'
        robj["message"] = "username or password is null"
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active: 
        auth.login(request, user)
        robj = r.hgetall("usr:" + username)
        robj["success"] = 'true'
        robj["message"] = "login is success" 
    else:
        if not r.exists("usr:"+username):        
            User.objects.create_user(username=username, email="" , password=password)
            r.hset("usr:" + username, "nm", username)
#             r.hset("usr:" + username, "email", email) 
            r.hset("usr:" + username, "crt_tms", time.time()) 
            r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
            r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
            robj["success"] = 'true'
            robj["message"] = "apply is success" 
            
            fllwkey="bmk:rd:1108470809:fllw"
            if r.exists(fllwkey):
                r.sadd(fllwkey,username) 
                r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|1108470809")
                r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|1108470809")
            
            fllwkey="bmk:rd:954189947:fllw"
            if r.exists(fllwkey):
                r.sadd(fllwkey,username) 
                r.zadd("usr:" + username+ ":fllw" ,time.time(), "rd|-|954189947")
                r.zadd("bmk:doc:share:byfllw",r.scard(fllwkey),"rd|-|954189947")
        else:    
            robj["success"] = 'false'
            robj["message"] = "login failed" 
            robj["data"] = []
    robj["api"]=api
    return HttpResponse(json.dumps(robj), mimetype="application/json")
    
def login_service(request):
    username = request.GET.get("usr", "");
    username = username.lower()
    password = request.GET.get("pwd", "");
    api = request.GET.get("api", "")
    robj = {}
    robj["api"]=api
    if username == "" or password == "":
        robj["success"] = 'false'
        robj["message"] = "username or password is null"
        robj["data"] = []
        return HttpResponse(json.dumps(robj), mimetype="application/json")
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active: 
        auth.login(request, user)
        robj = r.hgetall("usr:" + username)
        robj["success"] = 'true'
        robj["message"] = "apply is success" 
    else:
        robj["success"] = 'false'
        robj["message"] = "login failed" 
        robj["data"] = []
    robj["api"]=api
    return HttpResponse(json.dumps(robj), mimetype="application/json")
                                  
@csrf_protect
def login(request):
    """
    Create a login for a new customer.  
    """ 
    if  request.method == 'GET':
#        head_list = ['Duration', 'CURRENT YLD', 'PREV YLD', 'CHANGE', '1 WK YLD', '1 MO YLD', '6 MO YLD'];
#        t = loader.get_template('apply.html')
#        c = Context({
#            'head_list': head_list,
#        })
#        print request.get_full_path()
        return render_to_response('login.html',
                                  {'action': request.get_full_path()},
                                   context_instance=RequestContext(request))

    if  request.method == 'POST':
        username = request.POST.get("username", "");
        username = username.lower()
        password = request.POST.get("password", "");
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            log_typer(request, "login", "none")
            if not r.exists("usr:" + username):
                r.hset("usr:" + username, "nm", username) 
                r.hset("usr:" + username, "name", username) 
#            if not r.hexists("usr:" + username, "email"):
                r.hset("usr:" + username, "email", user.email) 
#            if not r.hexists("usr:" + username, "crt_tms"):
                r.hset("usr:" + username, "crt_tms", time.time()) 
#            if not r.hexists("usr:" + username, "fllw_bmk_cnt"):
                r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
#            if not r.hexists("usr:" + username, "fllw_bmk_cnt"):
                r.hset("usr:" + username, "fllw_bmk_cnt", 0) 
                
            request.session["otype"] = "login"
            
#            next = request.GET.get("next", "")
#            print next
#            if next != "":
#                return HttpResponseRedirect(next)
            return HttpResponseRedirect('/news/beaconnews') 
        else:
            return render_to_response('login.html', {'err_message': "登录失败!".decode("utf8")}, context_instance=RequestContext(request))
    #    return HttpResponseRedirect('/news/')
    #    return render_auth(request, 'apply.html', {'Customer' : lCustomer,'form' : lForm})
     
def logout(request):
    user = auth.logout(request)
#    return render_to_response('login.html', context_instance=RequestContext(request))
    return HttpResponseRedirect('/apply/login/')

def lostkey(request):
    user = auth.logout(request)
    if  request.method == 'GET': 
        return render_to_response('lostkey.html',
                                  {'action': request.get_full_path()},
                                   context_instance=RequestContext(request)) 
    if  request.method == 'POST':
        username = request.POST.get("username", "");
        email = request.POST.get("email", "");
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return render_to_response('lostkey.html', {'err_message': "错误的email格式!".decode("utf8")}, context_instance=RequestContext(request))
        if email != r.hget("usr:"+username,"email"):
            return render_to_response('lostkey.html', {'err_message': "无此用户,或者用户名与邮箱不匹配".decode("utf8")}, context_instance=RequestContext(request))
        token = id_generator(32)
        url= "http://"+request.META['HTTP_HOST']+"/apply/setnewpassword?token="+token
#        content=username+""",您好!\r\n欢迎您的注册,在访问过程中有任何疑问及建议可以给我们邮件或者在网站中提交建议,\r\n
#        现在,您可以邀请您的朋友们通过以下链接来指极星注册:\r\n  """.decode("utf8")+url
#         content="用户您好,已经收到了你的密码重置请求<br>\r\n\r\n请您点击此链接重新设置密码（链接将在 24 小时后失效）: <br><br>\r\n\r\n\r\n\r\n"
#         content+=url
#         content+="\r\n\r\n<br><br><br>这是一封系统邮件，请不要直接回复。"
#         sendemail(content,email,to_unicode_or_bust("指极星:设置新密码"))
        pushQueue("sendemail", username, "lostkey", tag=email, similarid="",urlstr=url)
        r.set("lostkey:"+token,username)
        r.expire("lostkey:"+token,86400)
        
    return render_to_response('login.html', {'err_message': "密码重置请求已经发送至邮箱,请在重设密码后登录".decode("utf8")}, context_instance=RequestContext(request))

def setnewpassword(request):
    if  request.method == 'GET': 
        token = request.GET.get("token", "");
        username = r.get("lostkey:"+token)
        if username is None:
            return render_to_response('setnewpassword.html', {'err_message': "错误的token或者token已过期,请重新申请密码重置!".decode("utf8")}, context_instance=RequestContext(request))
        return render_to_response('setnewpassword.html',
                                  {'action': request.get_full_path(),
                                  'token': token},
                                   context_instance=RequestContext(request)) 
    if  request.method == 'POST':
        password = request.POST.get("password", "");
        token = request.POST.get("token", "");
#         print token
        username = r.get("lostkey:"+token)
        quantity = log_typer(request, "setnewpassword", username)
        
        if username is None:
            return render_to_response('setnewpassword.html', {'err_message': "错误的token或者token已过期,请重新申请密码重置!".decode("utf8")}, context_instance=RequestContext(request))
        user = User.objects.get(username=username)
#         print user
        if user is None:
            return render_to_response('setnewpassword.html', {'err_message': "无此用户,是否邮箱未注册?".decode("utf8")}, context_instance=RequestContext(request))
#         user = users[0]
#         print user.username,"=====",password,"====="
        user.set_password(password)
        user.save()
        return render_to_response('login.html', {'err_message': "密码设置已成功,请登录".decode("utf8")}, context_instance=RequestContext(request))

def username_present(username):
    if User.objects.filter(username=username).count():
        return True
    
    return False
 
