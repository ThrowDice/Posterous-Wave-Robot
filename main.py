from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

import logging
import posterous

class MainPage(webapp.RequestHandler):
  def get(self):
    #logging.debug("home page")
    #self.response.out.write("Hello World!")
    posts = posterous.Posterous.all().order('-date').fetch(3)
    template_values = {'posts': posts}
    self.response.out.write(template.render('index.html',template_values)) 
    #for post in posts:
    #    self.response.out.write("%s wrote <a href='%s'>%s</a> at %s.<br/>" % (post.creator,post.url,post.title,post.date))
    

ROUTE = [('/', MainPage)]

application = webapp.WSGIApplication(ROUTE,debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

