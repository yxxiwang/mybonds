from django.conf import settings
from django.conf.urls.defaults import *
#from django.views.generic.simple import direct_to_template
import os
from django.contrib import admin
# from emailusernames.forms import EmailAuthenticationForm
# from registration.backends.default.urls import *
# from geeknews.forms import UserRegistrationForm  
admin.autodiscover() 
handler500 = "pinax.views.server_error" 
urlpatterns = patterns("",
    url(r"^$", 'mybonds.apps.geeknews.views.index', name="index"), 
    url(r'', include('django.contrib.auth.urls')), 
    url(r'^apply/$', 'mybonds.views.apply', name="apply"),
    url(r'^apply/login/$', 'mybonds.views.login', name="login"),
    url(r'^apply/lostkey/$', 'mybonds.views.lostkey', name="lostkey"),
    url(r'^apply/setnewpassword/$', 'mybonds.views.setnewpassword', name="setnewpassword"),
    url(r'^apply/logout/$', 'mybonds.views.logout', name="logout"),
    url(r'^apply/slogin/$', 'mybonds.views.login_service', name="login_service"), 
    url(r'^apply/sapply/$', 'mybonds.views.apply_service', name="apply_service"),
    url(r'^feedback/get_captcha/$', 'mybonds.views.get_captcha', name="get_captcha"),
    
    url(r'^groupmanage/$', 'mybonds.views.groupmanage', name="groupmanage"),
    url(r'^buddyhold/$', 'mybonds.views.buddyhold', name="buddyhold"),
    url(r'^usermodify/$', 'mybonds.views.user_modify', name="user_modify"),
    url(r'^sysparms/$', 'mybonds.views.sysparms', name="sysparms"),
    url(r'^character/$', 'mybonds.views.character', name="character"),
#    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
#                       
#    url(r"^index/$", direct_to_template, {"template": "index.html", }, name="index"),
#    # url(r'^examples/(?P<page_name>.*)/index.htm$', 'staticpage', name='static-pages'),
#
#    url(r"^dynamic/$", direct_to_template, {"template": "dynamic.html", }, name="home"),
    # url(r"^geeknews/$", direct_to_template, {"template": "geeknews.html",}, name="geeknews"),
    (r'^bonds/', include('bonds.urls')),
    (r'^news/', include('geeknews.urls')), 
    (r'^newsvc/', include('newsvc.urls')), 
    
    url(r"^admin/", include(admin.site.urls)),
     
) 
if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
