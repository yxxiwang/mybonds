#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import sys
import django.core.handlers.wsgi
os.chdir("/root/mybonds")
sys.path.append('/root') # path to your project ( if you have it in another dir).
sys.path.append('/root/mybonds') 
sys.path.append('/root/mybonds/apps') 


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mybonds.settings' # path to your settings module
    application = django.core.handlers.wsgi.WSGIHandler()
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8800)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
