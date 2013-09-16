#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import mimetypes
import time
import json
import redis
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import hashlib
from tornado.websocket import WebSocketHandler

r=redis.StrictRedis()

class Index(tornado.web.RequestHandler):
    def get(self):
        print "init "
        self.render('test.html')
        
class EchoWebSocket(WebSocketHandler):
    client = set()
    
    @staticmethod
    def send_to_all(message):
        for c in EchoWebSocket.client:
            c.write_message(message)
            
    def open(self):
        print "WebSocket opened"
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to WebSocket',
        }))
        hislist = r.zrevrange("chat",0,10)
        if hislist is not None or (hislist) >0: hislist.reverse() 
        for msg in hislist:
            mobj = json.loads(msg)
            self.write_message(json.dumps({
                'type': 'his',
                'message': "%s said %s" %(mobj["user"],mobj["message"]) ,
            }))
        EchoWebSocket.send_to_all({
            'type': 'sys',
            'message': 'user:'+ str(id(self)) + ' has joined',
        })
        EchoWebSocket.client.add(self)

    def on_message(self, message):
        r.zadd("chat",time.time(),json.dumps({"user":id(self),"message":message}) )
        EchoWebSocket.send_to_all({
            'type': 'user',
            'id': id(self),
            'message': message,
        })
        #self.write_message(u"You said: " + message+"\n")
        #time.sleep(3)
        #self.write_message(u"I give you again: " + message)

    def on_close(self):
        print "WebSocket closed"
        EchoWebSocket.client.remove(self)
        EchoWebSocket.send_to_all({
            'type': 'sys',
            'message': 'user:'+ str(id(self)) + ' has left',
        })

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "pngNewsDaily"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": True,
    "debug":True,
}

application = tornado.web.Application([
    (r"/", Index),
    #(r"/(.*)\.png", FileHandler),
    #(r"/([a-zA-Z0-9\-].+)", MainHandler),
    (r"/websocket", EchoWebSocket),
],**settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()