#coding=utf-8
from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document
from google.appengine.api import memcache
from google.appengine.ext import db
import postapi
import waveutil
import logging
#from types import *

class Posterous(db.Model):
    title = db.StringProperty()
    creator = db.StringProperty()
    wave_id = db.StringProperty()
    url = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def OnParticipantsChanged(properties, context):
  """Invoked when any participants have been added/removed."""
  added = properties['participantsAdded']
  for p in added:
    Notify(context)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added. Clear the root blip and
       add the form for posterous user to login."""
    logging.info("OnRobotAdded trigged.")
    #memcache.flush_all()
    root_wavelet = context.GetRootWavelet()
    creator = root_wavelet.GetCreator()
    if memcache.get(creator):
        #logging.info(memcache.get(creator))
        root_wavelet.CreateBlip().GetDocument().SetText(\
        """
        
Thanks for using the wave robot for posterous. \n\nEdit the root wavelet's title and body.Click done and then the wavelet will be posted to Posterous.com.
\nYou can change your post settings before posting a blog by replying '/site'.

Enjoy~
            """)
    else:
        blip = context.GetBlipById(root_wavelet.GetRootBlipId())
        logging.info("adding element")
        doc = blip.GetDocument() 
        doc.Clear()
        #doc.SetText("Please login using your posterous account.")
        doc.AppendElement(document.FormElement( \
            document.ELEMENT_TYPE.LABEL, \
            'subject_label', 'Email:')) 
        doc.AppendElement(document.FormElement( \
            document.ELEMENT_TYPE.INPUT, \
            'subject_input')) 
        doc.AppendElement(document.FormElement( \
            document.ELEMENT_TYPE.LABEL, \
            'description_lable', 'Password')) 
        doc.AppendElement(document.FormElement( \
            document.ELEMENT_TYPE.PASSWORD, \
            'description_input')) 
        doc.AppendElement(document.FormElement( \
            document.ELEMENT_TYPE.BUTTON, \
            'btn_update', 'Login to Posterous')) 

    

def OnFormButtonClicked(properties, context):
#ver 3.0
    logging.info("OnFormButtonClicked trigged.")
    root_wavelet = context.GetRootWavelet()
    creator = root_wavelet.GetCreator()
    logging.info("creator : %s" % creator)
    blip = context.GetBlipById(properties['blipId'])
    if not blip.IsRoot():
        for el in blip.GetElements().values():
            if el.type == "RADIO_BUTTON_GROUP":
                site_id = el.value.split(":")[0]
                name = el.value.split(":")[1]
                logging.info("site_id : %s" % site_id)
                ep = memcache.get(creator)
                email = ep.split(":")[0]
                password = ep.split(":")[1]
                ep = "%s:%s:%s:%s" % (email,password,site_id,name)
                logging.info(ep)
                memcache.set(creator, ep, 60*60*24)
                break
        blip.GetDocument().Clear()
        blip.GetDocument().SetText("\n\nYour settings have been saved. Now your blog will be posted to '%s'. Replying with '/site' to change your settings." % name)
    else:
        for el in blip.GetElements().values():
            #logging.info("%s : %s" % (el.type,el.value))
            if el.type==document.ELEMENT_TYPE.INPUT:
                email = el.value
            elif el.type==document.ELEMENT_TYPE.PASSWORD:
                password = el.value
        #logging.info("%s,%s" % (email,password))
        msg = postapi.AuthAUser(email,password)
        if msg == "OK":
            ep = "%s:%s" % (email,password)
            if not memcache.add(creator, ep, 60*60*24):
                logging.error("Memcache set failed.")
            else:
                logging.info("Memcache has been set for %s." % creator)
            blip.GetDocument().Clear()
            #root_wavelet.SetTitle("Title")
            #blip.GetDocument().SetText("Body")
            blip.GetDocument().SetText(\
                    """
                    
Now you can post through posterous robot. Start a new Wave and add posterous-robot@appspot.com as a paticipant.
            
Enjoy~
                        """)
            
            #root_wavelet.CreateBlip().GetDocument().SetText("I'm Posterous Robot.")
        else:
            root_wavelet.CreateBlip().GetDocument().SetText(msg)        
#ver 3.0
#ver 2.0
#    """memcache user's email and password for one day"""
#    logging.info("OnFormButtonClicked trigged.")
#    root_wavelet = context.GetRootWavelet()
#    creator = root_wavelet.GetCreator()
#    logging.info("creator : %s" % creator)
#    blip = context.GetBlipById(properties['blipId'])
#    for el in blip.GetElements().values():
#        #logging.info("%s : %s" % (el.type,el.value))
#        if el.type==document.ELEMENT_TYPE.INPUT:
#            email = el.value
#        elif el.type==document.ELEMENT_TYPE.PASSWORD:
#            password = el.value
#    #logging.info("%s,%s" % (email,password))
#    msg = postapi.AuthAUser(email,password)
#    if msg == "OK":
#        ep = "%s:%s" % (email,password)
#        if not memcache.add(creator, ep, 60*60*24):
#            logging.error("Memcache set failed.")
#        else:
#            logging.info("Memcache has been set for %s." % creator)
#        blip.GetDocument().Clear()
#        #root_wavelet.SetTitle("Title")
#        #blip.GetDocument().SetText("Body")
#        blip.GetDocument().SetText(\
#                """
#                
#Now you can post through posterous robot. Start a new Wave and add posterous-robot@appspot.com as a paticipant.
#        
#Enjoy~
#                    """)
#        
#        #root_wavelet.CreateBlip().GetDocument().SetText("I'm Posterous Robot.")
#    else:
#        root_wavelet.CreateBlip().GetDocument().SetText(msg)
#ver 2.0    

def OnBlipSubmitted(properties, context):
    logging.info("OnBlipSubmitted trigged.")
    blip = context.GetBlipById(properties['blipId'])
    wave_id = blip.GetWaveId()
    wavelet = context.GetWaveletById(blip.GetWaveletId())
    query = Posterous.all().filter('wave_id =', wave_id)
    logging.info("query.count() = %d" % query.count())
    if query.count()==0 and blip.IsRoot():
        contents = blip.GetDocument().GetText()
        title = wavelet.GetTitle()
        annotations = blip.GetAnnotations()
        logging.debug("logging annotations")
        #for annotation in annotations:
            #if annotation.name=="link/manual":
        #    logging.info("%s,%s,%s" % (annotation.name,annotation.value,annotation.range))
            #logging.debug(end_markup(annotation))
            #logging.debug(start_markup(annotation))
        #html = (list(convert(contents,annotations)))
        #logging.debug(html)
        #logging.debug("".join(html))
        #logging.debug(annotationTohtml(contents,annotations))
        creator = wavelet.GetCreator()
        ep = memcache.get(creator)
        if ep:
            ep = ep.split(":")    
            email = ep[0]
            password = ep[1]
            site_id = "0"
            if len(ep)>2:
                site_id = ep[2]
            contents = waveutil.annotationTohtml(contents,annotations)
            response = postapi.PostABlog(email,password,title,contents,site_id)
            #logging.info("response : %s" % response)
            if response:
                tiny_url = postapi.GetTinyUrl(response)
                wavelet.CreateBlip().GetDocument().SetText(\
                        "You just post a blog at %s" % (tiny_url))
                posterous = Posterous()
                posterous.creator = creator
                posterous.title = title#.encode("utf-8")
                posterous.url = tiny_url
                posterous.wave_id = blip.GetWaveId()
                posterous.put()
                logging.info("a new posterous saved.")
    elif query.count()==0:
#code for test 3.0
        #doc = blip.GetDocument()
        creator = wavelet.GetCreator()  
        ep = memcache.get(creator)
        contents = blip.GetDocument().GetText()
        contents = contents.replace(" ","")
        contents = contents.replace("\n","")
        if ep and contents == "/site":
            ep = ep.split(":")    
            email = ep[0]
            password = ep[1]  
            sites = postapi.GetSites(email,password)          
            logging.debug(sites)
            doc = wavelet.CreateBlip().GetDocument()
            doc.SetText("\n\n\nChoose the site you want to post to:\n\n\n")
            #.SetText("loading site setting")
            doc.AppendElement(document.FormElement( \
                        document.ELEMENT_TYPE.RADIO_BUTTON_GROUP, \
                        'site_choice_group')) 
            for site in sites:
                id,name = site
                doc.AppendElement(document.FormElement( \
                    document.ELEMENT_TYPE.RADIO_BUTTON, \
                    'site_choice_group',"%s:%s" % (id,name))) 
                doc.AppendElement(document.FormElement( \
                    document.ELEMENT_TYPE.LABEL, \
                    "%s:%s" % (id,name),name))
                doc.AppendText("\n")
            doc.AppendText("\n\n")            
            doc.AppendElement(document.FormElement( \
                        document.ELEMENT_TYPE.BUTTON, \
                        'save', 'Save your settings'))
    else:
        wavelet.CreateBlip().GetDocument().SetText("""

Sorry. Currently the Posterous API does not allow us to edit a post. If you want to post a new one, just start a new wave.

        """)
        
        
#        elements = blip.GetElements()
#        logging.debug("logging the element")
#        for element in elements:
#            logging.info(element)        
#            #logging.debug(element.value)
#code for test 3.0
#ver 2.0 code
#        wavelet.CreateBlip().GetDocument().SetText("""
#
#Sorry. Currently the Posterous API does not allow us to edit a post. If you want to post a new one, just start a new wave.
#
#        """)
#ver 2.0 code
           
 

        

def Notify(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")

if __name__ == '__main__':
    myRobot = robot.Robot('posterous-robot', 
      image_url='http://posterous-robot.appspot.com/assets/icon.png',
      version='0.015',
      profile_url='http://iposterous-robot.appspot.com/')
    #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
    myRobot.RegisterHandler(events.FORM_BUTTON_CLICKED, OnFormButtonClicked)
    myRobot.Run()
