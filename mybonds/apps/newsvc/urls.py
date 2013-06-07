#!/usr/bin/python
# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import *

urlpatterns = patterns('newsvc.views',
    url(r'^$', 'index', name="index"),
    url(r'^channels/$', 'channels', name="channels"),   
    url(r'^channelnews/$', 'channelnews', name="channelnews"),   
    url(r'^newsdetail/$', 'newsdetail', name="newsdetail"), 
    url(r'^removedocfromchannel/$', 'removeDocFromChannel', name="removeDocFromChannel"), 
    url(r'^grouplist/$', 'grouplist', name="grouplist"), 
    url(r'^channelsbygroup/$', 'channelsbygroup', name="channelsbygroup"), 
    url(r'^channelcounts/$', 'channelcounts', name="channelcounts"),  
    # upload lswdata 
)
