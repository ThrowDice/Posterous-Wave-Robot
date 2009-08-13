#coding=utf-8
import urllib
import urllib2
import base64
import logging
import re
from xml.etree import ElementTree

def PostABlog(email,password,title,body,site_id,autopost=1,tags=""):
    logging.info("PostABlog trigged.")
    logging.info("%s, %s" % (title,site_id))
    if title and body:
        title = title.encode("utf-8")
        body = body.encode("utf-8")
        site_id = site_id.encode("utf-8")
        posturl = "http://posterous.com/api/newpost"
        if site_id == "289080":
            data = "autopost=0&site_id=289080&title=%s&body=%s&source=google-wave-robot&sourceLink=http://posterous-robot.appspot.com/" % (title,body)
        elif site_id == "0":
            data = "title=%s&body=%s&source=google-wave-robot&sourceLink=http://posterous-robot.appspot.com/" % (title,body)
        else:
            data = "site_id=%s&title=%s&body=%s&source=google-wave-robot&sourceLink=http://posterous-robot.appspot.com/" % (site_id,title,body)
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
    authurl = "http://posterous.com/api/getsites"
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
 
def GetSites(email,password):
    authurl = "http://posterous.com/api/getsites"
    req = urllib2.Request(authurl)
    base64string = base64.encodestring(\
    '%s:%s' % (email, password))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    try:
        handle = urllib2.urlopen(req)
        rsp = handle.read()
        logging.info(rsp)
        root = ElementTree.fromstring(rsp)
        sites = []
        for site in root.findall("site"):
            sites.append((site.find("id").text,site.find("name").text))
        return sites
    except:
        return """
Invalid Posterous email or password."""

    
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
        
    