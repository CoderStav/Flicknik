from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.logger import Logger

from plyer import camera #object to read the camera

import base64
import os
import time

import requests

class submitScreen(Screen):
    """Base class for submitScreen"""

    media_path = ""
    mediaType = 0
    title = ""
    caption = ""
    uploads = 0
    
    def loadCamera(self, *largs):
        """Loads photo camera"""
        
        Logger.info("Photo Camera Loaded")
        self.mediaType = 0
        e = App.get_running_app().user_data_dir + '/flicknik_temp.jpg'
        if os.path.isfile(e):
            os.remove(e)
        camera.take_picture(e,self.done)
        
    def loadVideoCamera(self, *largs):
        """Loads video camera"""
    
        Logger.info("Video Camera Loaded")
        self.mediaType = 1
        e = App.get_running_app().user_data_dir + '/flicknik_temp.mp4'
        if os.path.isfile(e):
            os.remove(e)
        camera.take_video(e,self.done)
        
    def done(self, e):
        """Sets variables after media has been taken"""
        Logger.info("done function called")
        self.media_path = e
        
    def uploadInitialize(self):
        """Requests coordinates from app then sends user back to homeScreen. uploadToServer is run in a callback once coordinates are obtained"""
        Logger.info("flicknik: Initializing upload")
        self.uploads = 0
        self.title = self.ids.upload_title.text
        self.caption = self.ids.upload_caption.text
        self.ids.upload_title.text = ""
        self.ids.upload_caption.text = ""
        App.get_running_app().getCoordinates(True)
        App.get_running_app().screens.pop()
        Logger.info("flicknik: Returning to home")
        App.get_running_app().manager.current = "home"
        
    def uploadToServer(self):
        """Uploads media to server"""
        
        if(self.uploads == 0):
            self.uploads += 1
            Logger.info("flicknik: Uploading media...")
            url = App.get_running_app().backend + "submit.php?postType=submission"
            files = {'file': open(self.media_path, 'rb')}
            data = {'lat': App.get_running_app().lat, 'long': App.get_running_app().lon, 'userid': App.get_running_app().usrid, 'title': self.title, 'caption':self.caption, 'mediaType':self.mediaType}
            r = requests.post(url, files=files, data=data)
        
    def encodeFile(self):
        """Encodes media into base64 string for upload"""
    
        #temporary file to test uploading
        with open(self.media_path, "rb") as media_file:
            # reads image file and encodes it into base64
            encoded_string = base64.b64encode(media_file.read())  
        if not encoded_string:
            # encoded string is made an empty string if no data is found
            encoded_string = ''
            
        return encoded_string
