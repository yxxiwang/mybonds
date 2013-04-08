# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
import json
import csv,string
import sys
import redis

r = redis.StrictRedis(host='10.1.248.202',port=6379,db=0)
def index(request):
    #latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    print "bonds/index"
    t = loader.get_template('daily_bond_yc.html')
    date = request.GET.get("d","20120823")
    country = request.GET.get("ct","US")
    currency = request.GET.get("cu","USD")
    currency = currency.upper()
    rating = request.GET.get("rt","AAA")
    
    #reader = csv.reader(open("static/webdata/BOND_YC_USA_USD_yyyymmdd_AAA.csv"))
    list_bond = []
    #add head
    bonds = ("Duration","CURRENT YLD","PREV YLD","CHANGE","1 WK YLD","1 MO YLD","6 MO YLD")
    #list_bond.append(bonds)
    durations = ('1M','3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y')
    for dur in durations:
      #duration,current,last,change,weekAVG,days30AVG,days60AVG
      current = r.hget('YLD:USTB:'+currency+':GOV:DLY:'+dur, date)
      last = r.hget('YLD:USTB:'+currency+':GOV:DLY:'+dur, date)
      change = 0
      weekAVG = r.hget('YLD:USTB:'+currency+':GOV:AV1W:'+dur, date)
      days30AVG = r.hget('YLD:USTB:'+currency+':GOV:AV1M:'+dur, date)
      days60AVG = r.hget('YLD:USTB:'+currency+':GOV:AV6M:'+dur, date)
      bonds = (dur,current,last,change,weekAVG,days30AVG,days60AVG)
      list_bond.append(bonds)
    #for bonds in list_bond:
    # print bonds[0]
    if(date != ""):
      from datetime import datetime
      print date+";"
      date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
      
    c = Context({ 
        "list_bond": list_bond,
        "len_list_bond": len(list_bond),
        "date": date,
    })
    return HttpResponse(t.render(c))

def xhr_test(request):
    if request.is_ajax():
        if request.method == 'GET':
            message = "This is an XHR GET request"
        elif request.method == 'POST':
            message = "This is an XHR POST request"
            # Here we can access the POST data
            print request.POST
    else:
        message = "No XHR"
    return HttpResponse(message)

def detail(request, poll_id):
    #return HttpResponse("You're looking at poll %s." % poll_id)
    head_list = [('Duration','CURRENT YLD','PREV YLD','CHANGE','1 WK YLD','1 MO YLD','6 MO YLD'),
                 ('1-Month','1.12','0.22','1.1','1.1','2.2','2.1'),
                ];
    #writer = csv.writer(sys.stdout)
    writer = csv.writer(open("testcsv.data",'w'))
    for item in head_list:
      writer.writerow(item)

    response = HttpResponse()
    #response = HttpResponse(mimetype='text/csv')
    #response['Content-Disposition'] = 'attachment; filename=somefilename.csv'
    writer = csv.writer(response)

    reader = csv.reader(open("testcsv.data"),delimiter=",")
    #for title, year, director in reader:
    # print year, title
    # writer.writerow([year,title])
    for adr,acry,apry,cag,a1wy,a1my,a6my in reader:
      print adr,acry
      writer.writerow([adr,acry])
    return response


def mybonds(request, poll_id):
    #return HttpResponse("You're looking at the results of poll %s." % poll_id)
    head_list = ['Duration','CURRENT YLD','PREV YLD','CHANGE','1 WK YLD','1 MO YLD','6 MO YLD'];
    #head_list = {'Duration':'CURRENT YLD','PREV YLD':'CHANGE','1 WK YLD':'','1 MO YLD':'6 MO YLD'}
    encoded = json.dumps(head_list)
    response = HttpResponse(encoded, mimetype = "application/json")
    return response

def vote(request, poll_id):
    #return HttpResponse("You're voting on poll %s." % poll_id)
    head_list = ['Duration','CURRENT YLD','PREV YLD','CHANGE','1 WK YLD','1 MO YLD','6 MO YLD'];
    t = loader.get_template('daily/index.html')
    c = Context({
        'head_list': head_list,
    })
    return HttpResponse(t.render(c))

def mybonds(request, template_name="bonds/mybonds.html"):
    """
    lswdata for the currently authenticated user
    """ 
    userid = request.GET.get("userid","user111") 
    #r = redis.StrictRedis(host='10.1.248.202',port=6379,db=0)
    cdate = r.get('SYS:CRN:DATE')
    ctime = r.get('SYS:CRN:TIME')
    cdatetime = cdate+ctime
    cusips = r.hkeys('USER:POS:'+userid) 
    list_bond = []
    bonds = []
    
    def formatstr(fstr,pec=""):
    	if(str!=None):
    	  return '%.3f' % round(string.atof(fstr),3) +pec if(fstr != None) else None
    #durations = ('1M','3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y')
    #for amount,rating,maturity_date,coupon,eva_yield,eva_price,maket_value in mybonds:
    for cusip in cusips:
    	#print cusip
    	amount = r.hget('USER:POS:'+userid,cusip)
    	rating = r.hget('BOND:US:MUNI:RTG',cusip)
    	maturity_date = r.hget('BOND:US:MUNI:MAT',cusip)
    	coupon = r.hget('BOND:US:MUNI:CPN',cusip)
    	coupon = formatstr(coupon,"%")
    	eva_yield = r.hget('BOND:US:MUNI:YLD:'+cusip,cdatetime)
    	eva_yield = formatstr(eva_yield,"%")
    	eva_price = r.hget('BOND:US:MUNI:PRC',cusip)
    	#maket_value = r.hget('BOND:US:MUNI:MKTV:'+cusip,cdatetime)
    	maket_value = r.hget('USER:MKTV:'+userid,cusip)
    	maket_value = formatstr(maket_value)
    	bonds = (cusip,amount,rating,maturity_date,coupon,eva_yield,eva_price,maket_value)
    	list_bond.append(bonds) 
    	
    if(cdate != ""): 
      from datetime import datetime
      cdate = datetime.strptime(cdate, "%Y%m%d").strftime("%Y-%m-%d")
    #print len(list_bond)
    return render_to_response(template_name, {
        "list_bond": list_bond,
        "len_list_bond": len(list_bond),
        "cdate": cdate,
        "ctime": ctime,
    }, context_instance=RequestContext(request))
#index = login_required(index)


def realtime_bond_yc(request, template_name="bonds/realtime_bond_yc.html"):
    """
    realtime_bond_yc for the mvc return
    """
    date = request.GET.get("d","")
    country = request.GET.get("ct","US")
    currency = request.GET.get("cu","USD")
    currency = currency.upper()
    rating = request.GET.get("rt","AAA")
    duration = request.GET.get("dr","1M")
    #print "query"+query 
    #r = redis.StrictRedis(host='10.1.248.202',port=6379,db=0)
    cdate = r.get('SYS:CRN:DATE')
    ctime = r.get('SYS:CRN:TIME')
    cdatetime = cdate+" "+ctime+"00" 
    picname = "BOND_YC_USD/"+cdate+"/"+duration+"/"+ctime+".png"
    list_bond = []    
    #for duration,current,last,change,weekAVG,days30AVG,days60AVG in reader:
    #  bonds = (duration,current,last,change,weekAVG,days30AVG,days60AVG)
    #  list_bond.append(bonds)
    print picname
    return render_to_response(template_name, {
        "list_bond": list_bond,
        "len_list_bond": len(list_bond),
        "cdatetime": cdatetime,
        "cdate": cdate,
        "picname": picname,
    }, context_instance=RequestContext(request))

def daily_bond_yc(request, template_name="bonds/daily_bond_yc.html"):
    """
    daily_bond_yc for the mvc return
    """
    date = request.GET.get("d","20120823")
    country = request.GET.get("ct","US")
    currency = request.GET.get("cu","USD")
    currency = currency.upper()
    rating = request.GET.get("rt","AAA")
    #print "query"+query
    picname = "" 
    
    list_bond = [] 
    #r = redis.StrictRedis(host='10.1.248.202',port=6379,db=0)
    #reader = csv.reader(open("static/webdata/BOND_YC_USA_USD_yyyymmdd_AAA.csv")) 
    #add head
    bonds = (" ","CURRENT YLD","PREV YLD","CHANGE","1 WK YLD","1 MO YLD","6 MO YLD")
    list_bond.append(bonds)
    durations = ('1M','3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y')
    
    def formatstr(fstr): 
    	if(str!=None):
    	  return '%.3f' % round(string.atof(fstr),3) if(fstr != None) else None
    	  #return '%.3f' % round(string.atof(fstr),3) +"%" if(fstr != None) else None
    	  
    for dur in durations:
      #duration,current,last,change,weekAVG,days30AVG,days60AVG
      current = r.hget('YLD:USTB:'+currency+':GOV:DLY:'+dur, date)
      last = r.hget('YLD:USTB:'+currency+':GOV:LAST:'+dur, date)
      change =  string.atof(current)- string.atof(last) if(current != None and last != None) else None 
      change = formatstr(change)
      last = formatstr(last)
      current = formatstr(current)
      weekAVG = r.hget('YLD:USTB:'+currency+':GOV:AV1W:'+dur, date)
      weekAVG = formatstr(weekAVG)
      days30AVG = r.hget('YLD:USTB:'+currency+':GOV:AV1M:'+dur, date)
      days30AVG = formatstr(days30AVG)
      days60AVG = r.hget('YLD:USTB:'+currency+':GOV:AV6M:'+dur, date)
      days60AVG = formatstr(days60AVG) 
      
      bonds = (dur,current,last,change,weekAVG,days30AVG,days60AVG)
      list_bond.append(bonds)
    #for bonds in list_bond:
    # print bonds[0] 
    if(date != ""):
      picname = "BOND_YC_USA_USD_AAA_"+date+".png"
      from datetime import datetime
      date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
      
    return render_to_response(template_name, {
        "list_bond": list_bond,
        "len_list_bond": len(list_bond),
        "picname": picname,
        "date": date,
    }, context_instance=RequestContext(request))
#index = login_required(index)


def daily_bond_yc_html(request, template_name="daily_bond_yc.html"):
    """
    daily_bond_yc for the html return
    """
    resp = HttpResponse()
    date = request.GET.get("d","20120823")
    country = request.GET.get("ct","US")
    currency = request.GET.get("cu","USD")
    currency = currency.upper()
    rating = request.GET.get("rt","AAA") 

    list_bond_html ="""
    <TR>
        <th>Duration</th>
        <th>CURRENT YLD</th>
        <th>PREV YLD</th>
        <th>CHANGE</th>
        <th>1 WK YLD</th>
        <th>1 MO YLD</th>
        <th>6 MO YLD</th>
    </TR>
    """
    #YLD:USTB:USD:GOV:DLY:1M
    key = ""
    list_bond_html ="" 
    def formatstr(fstr): 
    	if(str!=None):
    	  return '%.3f' % round(string.atof(fstr),3) if(fstr != None) else None
    	  
    durations = ('1M','3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y')
    #durations = ('1M','3M' )
    for dur in durations:
      key = 'YLD:USTB:'+currency+':GOV:DLY:'+dur
      list_bond_html+= "<TR>"
      list_bond_html+= "<th>"+  dur  +"  </th> "
      list_bond_html+= "<TD>"+formatstr(r.hget(key,date)) +" </TD>  "
      list_bond_html+= "<TD>"+formatstr(r.hget(key,date)) +"</TD>  "
      list_bond_html+= "<TD>"+ "0"   +"</TD>  " 
      key = 'YLD:USTB:'+currency+':GOV:AV1W:'+dur
      list_bond_html+= "<TD>"+formatstr(r.hget(key,date)) +"</TD>" 
      key = 'YLD:USTB:'+currency+':GOV:AV1M:'+dur
      list_bond_html+= "<TD>"+formatstr(r.hget(key,date)) +"</TD>" 
      key = 'YLD:USTB:'+currency+':GOV:AV6M:'+dur
      list_bond_html+= "<TD>"+formatstr(r.hget(key,date)) +"</TD>"
      list_bond_html+= "</TR>"
    resp.write(list_bond_html)
    return resp


def resultdata(request):
    r = HttpResponse()
    import os
    from django.conf import settings
    #print (os.path.join(settings.STATIC_ROOT, "/webdata/b.csv"))
    #f = open(os.path.join(settings.STATIC_ROOT, "webdata","b.csv"))
    f = open("static/webdata/BOND_YC_USA_USD_yyyymmdd_AAA.csv")
    reader = csv.reader(f)
    r.write("<ROOT>")
    for duration,current,last,change,weekAVG,days30AVG,days60AVG in reader:
        print duration,current,last,change,weekAVG,days30AVG,days60AVG
        #r.write([org, year, risk,weights,loss_p,loss,ct_loss])
        r.write("<item>")
        r.write("<duration>"+duration+"</duration>")
        r.write("<current>"+current+"</current>")
        r.write("<last>"+last+"</last>")
        r.write("</item>")
    r.write("</ROOT>")
    return r
