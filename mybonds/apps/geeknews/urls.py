#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import *
#from django.conf.urls.defaults import include, patterns
urlpatterns = patterns('geeknews.views',
    url(r'^$', 'index', name="index"), 
    url(r'^init/([\w|\W]+)/$', 'init', name="init"),
    url(r'^load_seeds/$', 'load_seeds', name="load_seeds"),
    url(r'^load_similars/$', 'load_similars', name="load_similars"),
    url(r'^load_beacons/$', 'load_beacons', name="load_beacons"),
    url(r'^sfllowbeacon/$', 'fllowbeacon_service', name="fllowbeacon_service"),
    url(r'^slistbeacons/$', 'listbeacons_service', name="listbeacons_service"),
#    url(r'^get_cast_list/$', 'get_cast_list', name="get_cast_list"),
    url(r'^loaddata/$', 'retriveData', name="retriveData"), 
    url(r'^recomm/$', 'recomm', name="recomm"),
    url(r'^overview/$', 'overview', name="overview"),
    url(r'^navi/$', 'navi', name="navi"),
    url(r'^history/$', 'history', name="history"),
    url(r'^research/$', 'research', name="research"),
    url(r'^test/$', 'test', name="test"),
    url(r'^tagdoc/([\w|\W]+)/$', 'tagdoc', name="tagdoc"),
#    url(r'^tagdoc/$', 'tagdoc', name="tagdoc"),
    url(r'^feedbackform/$', 'feedbackform', name="feedbackform"),
    url(r'^feedback_reply/$', 'feedback_reply', name="feedback_reply"),
    url(r'^feedbacks/$', 'feedbacks', name="feedbacks"),
    
    url(r'^captchalist/$', 'captchalist', name="captchalist"),
    
    url(r'^beaconrelate/$', 'beaconRelate', name="beaconRelate"),
#     url(r'^beaconinit/$', 'beaconinit', name="beaconinit"),
    url(r'^beaconlist/$', 'beaconlist', name="beaconlist"),
    url(r'^beaconsave/$', 'beaconsave', name="beaconsave"),
    url(r'^beaconfilter/$', 'beaconfilter', name="beaconfilter"),
    url(r'^beacondelete/$', 'beacondelete', name="beacondelete"),
    url(r'^beaconcopy/$', 'beaconcopy', name="beaconcopy"),
    
    url(r'^mybeacons/$', 'mybeacons', name="mybeacons"),
    url(r'^beaconnews/$', 'beaconnews', name="beaconnews"),
#    url(r'^beaconnews/(\d+)/$', 'beaconnews', name="beaconnews"),
    url(r'^relatednews/$', 'relatednews', name="relatednews"),
    url(r'^globaltag/$', 'globaltag', name="globaltag"),
    url(r'^todaynews/$', 'todaynews', name="todaynews"),
    
    url(r'^listsimilar/$', 'listSimilarDoc', name="listSimilarDoc"), 
    url(r'^adm/$', 'admin', name="admin"),
    url(r'^search/$', 'searchs', name="searchs"),
    url(r'^sendemailfornews/$', 'sendemailfornews', name="sendemailfornews"),
    url(r'^sendemailforbeacon/$', 'sendemailforbeacon', name="sendemailforbeacon"),
#    url(r'^daemonstart/$', 'daemonStart', name="daemonStart"),
#    url(r'^daemonstop/$', 'daemonStop', name="daemonStop"),
#    url(r'^daemonrestart/$', 'daemonRestart', name="daemonRestart"),
    # upload lswdata 
)


urlpatterns += patterns('',
#    url(r'^lswdata/gateway/', 'lswdata.amfgateway.appGateway',name='lswdata_gate'),

)
