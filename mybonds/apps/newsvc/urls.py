# coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('newsvc.views',
    url(r'^$', 'index', name="index"),
    url(r'^channels/$', 'channels', name="channels"),   
    url(r'^channelnews/$', 'channelnews', name="channelnews"),   
    url(r'^newsdetail/$', 'newsdetail', name="newsdetail"), 
    # upload lswdata 
)

urlpatterns += patterns('',
#    url(r'^lswdata/gateway/', 'lswdata.amfgateway.appGateway',name='lswdata_gate'), 
)