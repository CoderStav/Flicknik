from kivy.app import App

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage

from kivy.logger import Logger

import urllib
import urllib2
import json

from jnius import autoclass
MediaPlayer = autoclass('android.media.MediaPlayer')

class photoScreen(Screen):
    """Base class for photoScreen"""
    
    def setContent(self, postid, source_url, isVideo):
        """Sets content data for photoScreen"""
        
        if(isVideo == True):
            pass
        else:
            img = AsyncImage(source=source_url)
            Logger.info('Image loaded! {}.jpg'.format(postid))
            self.ids.fullimg_holder.add_widget(img)

class fullviewScreen(Screen):
    pass

def photoHandle(postid,source_url,isVideo):
    """Creates a photoScreen, adds it to the ScreenManager, and switches to it"""
    
    if App.get_running_app().manager.has_screen(postid) is False:
        scrn = photoScreen()
        scrn.setContent(postid, source_url, isVideo)
        scrn.name = postid
        App.get_running_app().manager.add_widget(scrn)
    App.get_running_app().changeScreen(postid)
