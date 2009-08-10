#coding=utf-8
import urllib
import urllib2
import base64
import logging
import re

def PostABlog(email,password,site_id,title,body,tags=""):
    logging.info("PostABlog trigged.")
    logging.info("title : %s" % title)
    logging.info("body : %s" % body)
    if title and body:
        title = title.encode("utf-8")
        body = body.encode("utf-8")
        logging.info("body : %s" % body)
        body = body.replace("\n","<br/>")
        posturl = "http://posterous.com/api/newpost"
        data = "title=%s&body=%s&source=wave-robot&sourceLink=http://blog.kangye.org" % (title,body)
        req = urllib2.Request(posturl)
        base64string = base64.encodestring(\
        '%s:%s' % (email, password))[:-1]
        authheader =  "Basic %s" % base64string
        req.add_header("Authorization", authheader)
        handle = urllib2.urlopen(req,data)
        response = handle.read()
        logging.info(response)
        return response
    else:
        logging.info("Title or body missed.")

def AuthAUser(email,password):
    authurl = "http://posterous.com/api/newpost"
    req = urllib2.Request(authurl)
    base64string = base64.encodestring(\
    '%s:%s' % (email, password))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    try:
        handle = urllib2.urlopen(req)
        return "OK"
    except:
        return """
Invalid Posterous email or password."""
#    response = handle.read()
#    if response.index("stat=\"ok\"") == -1:
#        return "OK"
#    else:
#        msg = response.index("msg")
#        quote = response.index("\"",msg+5)
#        msg = response[msg+5,quote]
#        return msg
     
    
def GetTagsByTitle(title):
    pattern = "((tags:.*))$"
    if re.search(pattern,title):
        tags = re.search(pattern,title).group()
        tags = tags.replace("tags:","")
        tags = tags.replace("))","")
        logging.info("tags:%s" % tags)
        index = title.index("((tags:")
        title = title[:index]
        return (title.encode("utf-8"),tags.encode("utf-8"))
    else:
        return (title,"From-Wave")
    
def GetTinyUrl(response):
    start = response.index("<url>")
    end   = response.index("</url>")
    tiny_url = response[start+5:end]
    return tiny_url
        
    