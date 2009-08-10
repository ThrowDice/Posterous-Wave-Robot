#coding=utf-8
from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document
from google.appengine.api import memcache
from google.appengine.ext import db
import postapi
import logging

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
        
Thanks for using wave robot for posterous. Edit the root wavelet's title and body.Click done and then the wavelet will be posted to Posterous.com.

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
    """memcache user's email and password for one day"""
    logging.info("OnFormButtonClicked trigged.")
    root_wavelet = context.GetRootWavelet()
    creator = root_wavelet.GetCreator()
    logging.info("creator : %s" % creator)
    blip = context.GetBlipById(properties['blipId'])
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
        creator = wavelet.GetCreator()
        ep = memcache.get(creator)
        if ep:
            ep = ep.split(":")    
            email = ep[0]
            password = ep[1]
            response = postapi.PostABlog(email,password,289080,title,contents)
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
    elif query.count()==1:
        wavelet.CreateBlip().GetDocument().SetText("""

Sorry. Currently the Posterous API does not allow us to edit a post. If you want to post a new one, just start a new wave.

        """)
            #else:
            #    wavelet.CreateBlip().GetDocument().SetText("Your blog's title or body should not be la")
            
        
        

def Notify(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")

if __name__ == '__main__':
    myRobot = robot.Robot('posterous-robot', 
      image_url='http://posterous-robot.appspot.com/assets/icon.png',
      version='0.014',
      profile_url='http://iposterous-robot.appspot.com/')
    #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
    myRobot.RegisterHandler(events.FORM_BUTTON_CLICKED, OnFormButtonClicked)
    myRobot.Run()
