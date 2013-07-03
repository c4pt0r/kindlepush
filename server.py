#!/usr/bin/env python
#encoding=utf-8
import tornado.ioloop
import tornado.web
import kindlepush
import redis
import json
import time

r = redis.Redis("localhost", port = 6379, db = 0)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class PushLinkHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument("url")
        sendto = self.get_argument("sendto")
        title = self.get_argument("title")
        ts = time.time()
        r.lpush("push_tasks", json.dumps({'url':url, 'sendto': sendto, 'title': title, 'ts':ts}))
        self.write(json.dumps({"ret":0}))

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/pushlink", PushLinkHandler)
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
