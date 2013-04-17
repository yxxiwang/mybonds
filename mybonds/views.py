#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
import json
import csv, string
import sys, time
import redis
#from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.contrib import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
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
    password = request.GET.get("pwd", "");
    email = request.GET.get("email", "");
    captcha = request.GET.get("captcha", "");
    robj = {}
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
    saveCaptcha(id_generator())
    saveCaptcha(id_generator())
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        robj["success"] = 'true'
        robj["message"] = "apply is success" 
        robj["data"] = r.hgetall("usr:" + username)
        greeting_typer(username, "apply", username)
    else:
        robj["success"] = 'false'
        robj["message"] = "disabled account!" 
        robj["data"] = []
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
        password = request.POST.get("password", "");
        email = request.POST.get("email", "yxxiwang@gmail.com");
        captcha = request.POST.get("captcha", "111111");
        if username == "" or password == "" or email == "" or captcha == "" or len(username)>10: 
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
            saveCaptcha(id_generator())
            saveCaptcha(id_generator())
            
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                log_typer(request, "apply", "none")
                greeting_typer(username, "apply", username)
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
    robj={}
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
        
@login_required
def groupmanage(request):
    optype = request.GET.get("o", "")
    acttype = request.GET.get("a", "list")
    username = getUserName(request)
    robj={}
    if optype =="service":
        if acttype == "list":
            email = request.GET.get("email", "")
            groups = r.zrevrange("usr:"+username+":group:lst",0,-1)
            group_list=[]
            for groupid in groups:
                groupobj=r.hgetall("usr:"+username+":group:"+groupid)
                groupobj["groupid"]=groupid
                if not email=="":
                    if r.zscore("usr:"+username+":buddy:"+groupid,email) is None:
                        groupobj["hasemail"]="0" 
                    else:
                        groupobj["hasemail"]="1"  
                else:
                    groupobj["hasemail"]=str(r.zcard("usr:"+username+":buddy:"+groupid))
                group_list.append(groupobj)
#            group_list.append({"groupid":"all","groupname":"all"})
            robj["groups"] = group_list
            robj["success"] = 'true'
            robj["message"] = "list group is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        elif acttype == "add": 
            groupname = request.GET.get("groupname", "")
            if groupname !="":
                groupid = getHashid(groupname)
                r.zadd("usr:"+username+":group:lst",time.time(),groupid)
                r.hset("usr:"+username+":group:"+groupid,"groupname",groupname)  
                robj["groupid"]=groupid 
            robj["groupname"]=groupname  
            robj["groupid"]=groupid  
            robj["success"] = 'true'
            robj["message"] = "add group is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        elif acttype == "delete":
            groupid = request.GET.get("groupid", "")
            groupname=""
            if groupid !="":
                groupname=r.hget("usr:"+username+":group:"+groupid,"groupname")
                r.zrem("usr:"+username+":group:lst",groupid)
                r.delete("usr:"+username+":group:"+groupid)
                r.delete("usr:"+username+":buddy:"+groupid)
            robj["groupid"]=groupid
            robj["groupname"]=groupname
            robj["success"] = 'true'
            robj["message"] = "delete group is success"
            return HttpResponse(json.dumps(robj), mimetype="application/json")
            
    else:
        return HttpResponse("ok")
        

@login_required
def user_modify(request,template_name="beacon/usermodify.html"): 
    optype = request.GET.get("o", "");
#    username = request.GET.get("u", "");
    username = getUserName(request)
    password = request.GET.get("pwd", "");
    newpwd = request.GET.get("newpwd", "");
    displayname = request.GET.get("name", "");
    email = request.GET.get("email", "");
    rssuser = request.GET.get("rssuser", "");
    robj={}
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
                r.hset("usr:" + username, "name", displayname)
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
            return HttpResponse(json.dumps(robj), mimetype="application/json")
        else:
            email = r.hget("usr:"+username,"email")
            name = r.hget("usr:"+username,"name")
            return render_to_response(template_name, {
                'username':username,
                'email':email,
                'current_path': request.get_full_path(),
            }, context_instance=RequestContext(request))
    if  request.method == 'POST':
        displayname = request.POST.get("username", "");
        password = request.POST.get("password", "");
        email = request.POST.get("email", "");
        
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
    
def login_service(request):
    username = request.GET.get("usr", "");
    password = request.GET.get("pwd", "");
    robj = {}
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

def username_present(username):
    if User.objects.filter(username=username).count():
        return True
    
    return False
 
