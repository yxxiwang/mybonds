# coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('bonds.views',
    url(r'^$', 'index', name="index"),
    url(r'^daily_bond_yc/$', 'daily_bond_yc', name="bonds_dataindex"),   
    url(r'^daily_bond_yc_html/$', 'daily_bond_yc_html', name="daily_bond_yc_html"),
    url(r'^realtime_bond_yc/$', 'realtime_bond_yc', name="realtime_bond_yc"),   
    url(r'^mybonds/$', 'mybonds', name="mybonds"),   
    url(r'^resultdata/$', 'resultdata', name="resultdata"),
    # upload lswdata 
)

urlpatterns += patterns('',
#    url(r'^lswdata/gateway/', 'lswdata.amfgateway.appGateway',name='lswdata_gate'),

)