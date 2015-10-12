from kivy.app import App
from kivy.core.window import Window

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.graphics import *
from kivy.logger import Logger
from kivy.metrics import dp

from customObjects import imageButtonLocal
from voteFuncs import vote, updateVoteDisplay

from kivy.network.urlrequest import UrlRequest

import urllib
import urllib2
import json
import time
    
def formatTime(t):
    """Formats epoch time into readable form"""

    u = "seconds"
    if t > 60:
        t = t/60
        u = "minutes"
        if t > 59:
            t = t/60
            u = "hours"
            if t > 23:
                t = t/24
                u = "days"
                if t > 6:
                    t = t/7
                    u = "weeks"
                    if t > 3:
                        t = t/4.3333
                        u = "months"
                        if t > 11:
                            t = t/12
                            u = "years"
    
    if t <= 1:
        u = u[0:-1]
    
    return "{} {} ago".format(int(t), u)


class replyCell(FloatLayout):
    """Base layout for all reply bodies"""
    
    def __init__(self, replyid, body, voteCount, previousvote, uname, ucolor, timestamp, tint, *args, **kwargs):
        super(replyCell, self).__init__(**kwargs)
        
        previousvote = int(previousvote)
        
        timeSincePost = int(time.time()) - int(timestamp)
        
        UserColor = ucolor.split(',');
        
        if tint == True:
            with self.canvas:
                Color(0.78823529411, 0.78823529411, 0.78823529411, 0.35)
                self.background = Rectangle(size=self.size, pos=self.pos)
           
            self.bind(pos=self.updateCanvas, size=self.updateCanvas)
        
        replyBody = Label(text=body, pos_hint={'x':0.0175, 'center_y':0.55}, size_hint=(0.7, 0.9), text_size=(dp(250), dp(90)), font_size="15sp", color=(0,0,0,1), halign="left", valign="middle")
        
        username = Label(text=uname, pos_hint={'x':0.0175, 'y':0.0175}, size_hint=(0.7, 0.3), text_size=(dp(250), dp(35)), font_size="13sp", color=(float(UserColor[0]), float(UserColor[1]), float(UserColor[2]), 0.5), halign="left")
        
        votes = Label(text=voteCount, pos_hint={'right':0.9825, 'center_y':0.5}, size_hint=(0.25, None), text_size=(None, None), font_size="20sp", color=(0,0,0,1))
        voteButtons = BoxLayout(orientation="horizontal", size_hint=(0.25, 0.25), pos_hint={'right':0.9825, 'y':0.05})
        
        upvote = imageButtonLocal(source="", size_hint_x=0.5)
        downvote = imageButtonLocal(source="", size_hint_x=0.5)
        
        if previousvote != 0:
            if previousvote == 1:
                upvote.source = "data/up_clicked.png"
                upvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, 0))
                downvote.source = "data/down_unclicked.png"
                downvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, -2))
            else:
                upvote.source = "data/up_unclicked.png"
                upvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, 2))
                downvote.source = "data/down_clicked.png"
                downvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, 0))
                                               
        else:
            upvote.source = "data/up_unclicked.png"
            upvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, 1))
            downvote.source = "data/down_unclicked.png"
            downvote.bind(on_press=lambda vtcnt: updateVoteDisplay(upvote, downvote, votes, voteCount, -1))
        
        upvote.bind(on_press=lambda upvt: vote(App.get_running_app().backend, App.get_running_app().usrid, replyid, "upvote", "reply"))
        downvote.bind(on_press=lambda dnvt: vote(App.get_running_app().backend, App.get_running_app().usrid, replyid, "downvote", "reply"))
        
        voteButtons.add_widget(upvote)
        voteButtons.add_widget(downvote)
        
        timeSince = Label(text=formatTime(timeSincePost), pos_hint={'right':0.9825, 'top':0.9825}, size_hint=(0.7, 0.25), text_size=(dp(250), dp(35)), font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5), halign="right", valign="top")
        
        self.add_widget(replyBody)
        self.add_widget(username)
        self.add_widget(votes)
        self.add_widget(voteButtons)
        self.add_widget(timeSince)
        
    def updateCanvas(self, *args):
        with self.canvas:
            self.background.pos = self.pos
            self.background.size = self.size

class captionCell(BoxLayout):
    """Base layout for caption body"""
    
    def __init__(self, caption, *args, **kwargs):
        super(captionCell, self).__init__(**kwargs)
        
        with self.canvas:
            Color(0.78823529411, 0.78823529411, 0.78823529411, 0.35)
            self.background = Rectangle(size=self.size, pos=self.pos)
           
        self.bind(pos=self.updateCanvas, size=self.updateCanvas)
        
        captionBody = Label(text=caption, text_size=(dp(250), dp(90)), font_size="15sp", color=(0,0,0,1), halign="center", valign="middle")

        self.add_widget(captionBody)
        
    def updateCanvas(self, *args):
        with self.canvas:
            self.background.pos = self.pos
            self.background.size = self.size
        

class replyScreen(Screen):
     """Base class for replyScreen"""
     
     def overlayMessage(self, show, *args):
        """Initializes a message in the overlay, 0 - loading, 1 - blank, 2 - No posts, 3 - server unavailable"""
        if show == 0:
            self.ids.replyscr_statusmsg.text = "Loading replies..."
        elif show == 1:
            self.ids.replyscr_statusmsg.text = ""
        elif show == 2:
            self.ids.replyscr_statusmsg.text = "No replies found, be the first!"
        elif show == 3:
            self.ids.replyscr_statusmsg.text = "Server unavailable :("
     
     def defineVals(self, pid, OP):
        """Sets original post data so replyScreen can display the proper information. Also binds keyboardMode to the keyboard."""
        
        self.postid = pid
        self.originalPost = OP
        
     def setOP(self, *args, **kwargs):
        """Clears replyScreen's output and inserts original post at the top of the replyScreen"""
        
        self.ids.replyscr_output.clear_widgets()
        self.ids.replyscr_output.add_widget(self.originalPost)
        
     def keyboardMode(self, *args, **kwargs):
        """Moves text input to a readable position when soft keyboard is up"""
        
        if Window.keyboard_height > 0:
            self.ids.replyscr_bottombar.pos_hint = {'center_y':0.395}
        else:
            self.ids.replyscr_bottombar.pos_hint = {'y':0}
     
     def submitReply(self):
        """Submits reply to server"""
        
        if len(self.ids.replyscr_replyfield.text) > 0:
            url = App.get_running_app().backend + "submit.php?postType=reply"
            values = {"body" : self.ids.replyscr_replyfield.text, "userid" : App.get_running_app().usrid, "postid" : self.postid}
            headers = {"Content-type" : "application/x-www-form-urlencoded"}
            data = urllib.urlencode(values)
            binary_data = data.encode("ascii")
            UrlRequest(url, req_body=binary_data, req_headers=headers, on_success=self.display)
            
            body = self.ids.replyscr_replyfield.text
            
            self.ids.replyscr_replyfield.text = ""
     
     def processReplies(self, request, result, *args, **kwargs):
        """Processes data into replyCells and puts them into replyScreen's ScrollView"""
        
        self.ids.replyscr_output.clear_widgets()
        
        self.ids.replyscr_output.add_widget(self.originalPost) # Puts original post postCell into output first before processing data
        
        if len(self.originalPost.Caption) > 0:
            self.ids.replyscr_output.add_widget(captionCell(self.originalPost.Caption))
        
        i = 1
        connectionError = False
        try:
            jsonResponse = json.loads(result)
            jsonData = jsonResponse["Data"]
                
            for reply in jsonData:
                Body = reply["body"]
                Votes = reply["votes"]
                Replyid = reply["replyid"]
                Uname = reply["name"]
                Ucolor = reply["color"]
                Timestamp = reply["timestamp"]
                Previousvote = reply["previousvote"]
                
                if i%2 == 0:
                    replyFormat = replyCell(Replyid, Body, Votes, Previousvote, Uname, Ucolor, Timestamp, True)
                else:
                    replyFormat = replyCell(Replyid, Body, Votes, Previousvote, Uname, Ucolor, Timestamp, False)
                
                self.ids.replyscr_output.add_widget(replyFormat)
                i += 1
            self.ids.replyscr_output.add_widget(FloatLayout())
            self.ids.replyscr_output.add_widget(FloatLayout())
        except:
            self.overlayMessage(3)
            connectionError = True
        
        if connectionError == False:
            if i > 1:
                self.overlayMessage(1)
            else:
                self.overlayMessage(2)
        
     def display(self, *args, **kwargs):
        """Base function for displaying content on the replyScreen"""
        
        self.overlayMessage(0)
        
        url = App.get_running_app().backend + "replies.php"
        values = {"userid":App.get_running_app().usrid, "postid":self.postid}
        headers = {"Content-type" : "application/x-www-form-urlencoded"}
        data = urllib.urlencode(values)
        binary_data = data.encode("ascii")
        
        UrlRequest(url, req_body=binary_data, req_headers=headers, on_success=self.processReplies, on_failure=self.processReplies)
            
        
                
