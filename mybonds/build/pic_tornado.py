#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import mimetypes

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import hashlib
# import tornado.web.RequestHandler

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")

class MainHandler(tornado.web.RequestHandler):
     def get(self,picdir="pngNewsDaily"):
        print "====MainHandler=get===%s" % picdir
        #          print self.get_argument("dir")
        piclist = os.listdir(picdir)
#         piclist.sort()
        piclist.sort(key=lambda x: os.path.getmtime(picdir+"/"+x))
        piclist = [picname for picname in piclist  if picname.endswith(".png") or picname.endswith(".jgp")]
#         items = ["test.png", "test.png", "test.png"] 
        self.render("index.html", title="Tornado, Python Server", piclist=piclist,picdir=picdir)

class FileHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, path,include_body=True):
        print "FileHandler=get===%s.png" % path
        if not path:
            path = 'index.html'
        else:
            path = path+".png"
 
        if not os.path.exists(path):
            raise tornado.web.HTTPError(404)

        mime_type = mimetypes.guess_type(path)
#         print mime_type
        self.set_header("Content-Type", mime_type[0] or 'text/plain')
 
        with open(path, "rb") as file:
            data = file.read()
            hasher = hashlib.sha1()
            hasher.update(data)
            self.set_header("Etag", '"%s"' % hasher.hexdigest())
            if include_body:
                self.write(data)
            else:
                assert self.request.method == "HEAD"
                self.set_header("Content-Length", len(data))
                
#         outfile = open(path)
#         for line in outfile:
#             self.write(line)
        self.finish()
        
class StoryHandler(tornado.web.RequestHandler):
    def get(self, story_id):
        self.write("You requested the story " + story_id)
        
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "pngNewsDaily"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": True,
    "debug":True,
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/(.*)\.png", FileHandler),
    (r"/([a-zA-Z0-9\-].+)", MainHandler),
    (r"/story/([0-9]+)", StoryHandler),
#     (r"/pngNewsDaily/([a-zA-Z0-9\-]+\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
],**settings)


if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()


