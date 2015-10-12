from kivy.app import App

from kivy.clock import Clock

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage
from kivy.uix.togglebutton import ToggleButton

from kivy.properties import ListProperty, AliasProperty
from kivy.graphics import *
from kivy.logger import Logger
from kivy.metrics import dp

from plyer import gps

from screen_fullview import photoHandle
from screen_reply import replyScreen
from customObjects import imageButton, imageButtonLocal, labelButton
from voteFuncs import vote, updateVoteDisplay

from kivy.network.urlrequest import UrlRequest

import urllib
import urllib2
import json
import time


def getReplyScreen(postid, title, voteCount, previousvote, img, source_url, timestamp, mediaType, caption):
    """Creates and switches to the reply screen of a given post"""
    
    if App.get_running_app().manager.has_screen("reply_" + postid) is False:
        
        img2 = imageButton(source=img.source)
        originalPost = postCell(postid, title, voteCount, previousvote, img2, source_url, timestamp, mediaType, caption, True)
        
        scrn = replyScreen()
        scrn.defineVals(postid, originalPost)
        scrn.name = "reply_" + postid
        App.get_running_app().manager.add_widget(scrn)
        
    App.get_running_app().changeScreen("reply_" + postid)
    App.get_running_app().manager.get_screen("reply_" + postid).setOP()
    Clock.schedule_once(App.get_running_app().manager.get_screen("reply_" + postid).display, 0.5)

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

class notifyPopup(BoxLayout):
    """Creates a multi-use popup prompt in the postCell body"""
    
    def __init__(self, notificationType, pid, *args, **kwargs):
        super(notifyPopup, self).__init__(**kwargs)
        
        self.category = None;
        
        with self.canvas:
            Color(0.14901960784, 0.57647058823, 1, 1)
            self.background = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.updateCanvas, size=self.updateCanvas)
        
        if notificationType == "report":
            # creating the toggle buttons that determine the category of the report
            toggleButtonHolder = BoxLayout(orientation="horizontal", size_hint_y=0.6)
            gruesome = ToggleButton(text="Gruesome", group="report", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            gruesome.bind(on_press=lambda setcat: self.setCategory(0))
            childAbuse = ToggleButton(text="Child abuse", group="report", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            childAbuse.bind(on_press=lambda setcat: self.setCategory(1))
            spam = ToggleButton(text="Spam", group="report", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            spam.bind(on_press=lambda setcat: self.setCategory(2))
            toggleButtonHolder.add_widget(gruesome)
            toggleButtonHolder.add_widget(childAbuse)
            toggleButtonHolder.add_widget(spam)
            
            # creating the cancel/report buttons
            buttonHolder = BoxLayout(orientation="horizontal", size_hint_y=0.4)
            cancelButton = Button(text="Cancel", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            cancelButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            cancelButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            reportButton = Button(text="Report", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            reportButton.bind(on_press=lambda reportpost: self.submitReport(self.category, pid))
            reportButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            reportButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            buttonHolder.add_widget(cancelButton)
            buttonHolder.add_widget(reportButton)
            
            self.add_widget(toggleButtonHolder)
            self.add_widget(buttonHolder)
        elif notificationType == "block":
            
            blockPrompt = Label(text="Block this user?", font_size="15sp", color=(1,1,1,1), size_hint_y=0.6)
            
            # creating the button holder containing the Yes/No buttons
            buttonHolder = BoxLayout(orientation="horizontal", size_hint_y=0.4)
            noButton = Button(text="No", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            noButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            noButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            yesButton = Button(text="Yes", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            yesButton.bind(on_press=lambda blockuser: self.submitBlock(pid))
            yesButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            yesButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            buttonHolder.add_widget(noButton)
            buttonHolder.add_widget(yesButton)
            
            self.add_widget(blockPrompt)
            self.add_widget(buttonHolder)
        elif notificationType == "hide":
         
            hidePrompt = Label(text="Hide this post?", font_size="15sp", color=(1,1,1,1), size_hint_y=0.6)
            
            # creating the button holder containing the Yes/No buttons
            buttonHolder = BoxLayout(orientation="horizontal", size_hint_y=0.4)
            noButton = Button(text="No", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            noButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            noButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            yesButton = Button(text="Yes", background_normal = '', background_color=[0.11764705882352941, 0.4588235294117647, 0.8, 1])
            yesButton.bind(on_press=lambda blockuser: self.submitHide(pid))
            yesButton.bind(on_press=lambda clearprompt: self.clear_widgets())
            yesButton.bind(on_press=lambda clearbg: self.updateCanvas(True))
            buttonHolder.add_widget(noButton)
            buttonHolder.add_widget(yesButton)
            
            self.add_widget(hidePrompt)
            self.add_widget(buttonHolder)
        
    def submitReport(self, cat, postid):
        """Submits reports to the server"""
        
        if cat == None:
            return
            
        url = App.get_running_app().backend + "report.php"
            
        values = {"userid_reporter":App.get_running_app().usrid, "postid":postid, "category":cat}
                
        headers = {"Content-type" : "application/x-www-form-urlencoded"}
        data = urllib.urlencode(values)
        binary_data = data.encode('ascii')
        UrlRequest(url, req_body=binary_data, req_headers=headers)
    
    def submitBlock(self, postid):
        """Submits user block request to server"""
        url = App.get_running_app().backend + "block.php"
            
        values = {"userid":App.get_running_app().usrid, "postid":postid}
                
        headers = {"Content-type" : "application/x-www-form-urlencoded"}
        data = urllib.urlencode(values)
        binary_data = data.encode('ascii')
        UrlRequest(url, req_body=binary_data, req_headers=headers)
        
    def submitHide(self, postid):
        """Submits post hide request to server"""
        url = App.get_running_app().backend + "hide.php"
            
        values = {"userid":App.get_running_app().usrid, "postid":postid}
                
        headers = {"Content-type" : "application/x-www-form-urlencoded"}
        data = urllib.urlencode(values)
        binary_data = data.encode('ascii')
        UrlRequest(url, req_body=binary_data, req_headers=headers)
    
    def updateCanvas(self, clearwidget=False, *args):
        if clearwidget == True:
            with self.canvas:
                Color(1,1,1,0)
                self.background.size = (0,0)
        else:
            with self.canvas:
                self.background.pos = self.pos
                self.background.size = self.size

    def setCategory(self, val):
        """Sets the value of category"""
        self.category = val
            

class sponsoredCell(FloatLayout):
    """Base layout for sponsored posts"""
    
    # TODO 
    # Sponsored posts AKA ads
    # Display them at the top of homeScreen
    # Have advertiser choose a centerpoint location for their ad campaign and then define a radius
    # Organize into MYSQL sponsored_tbl with Title, Link, Image Location (use a default if none specified/uploaded), lat, lon, radius from lat/lon, keywords (future usage), and remaining impressions
    # Every time an ad is queried from the table, subtract impressions by 1
    # If no ads applicable to the user can be found, display nothing
    
    def __init__(self, postid, title, link, img=None, *args, **kwargs):
        super(sponsoredCell, self).__init__(**kwargs)
        
        with self.canvas:
            Color(0.11764705882352941, 0.4588235294117647, 0.8, 0.35)
            self.background = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(pos=self.updateCanvas, size=self.updateCanvas)
        
        imgholder = BoxLayout(orientation="horizontal", size_hint=(0.25, 1), pos_hint={'right':0.2625, 'top':1})
        
        if img != None:
            imgholder.add_widget(img)
        else:
            imgholder.add_widget(Image(source="data/defaultSponsoredThumbnail.png")) # temporary placeholder image

    
        postTitle = Label(text=title, pos_hint={'center_x':0.57, 'top':0.7}, size_hint=(0.5, None), text_size=(400, 150), font_size="15sp", color=(0,0,0,1), halign="left", valign="middle")
        
        sponsoredLabel = Label(text="Sponsored", pos_hint={'right':0.9825, 'top':0.9825}, size_hint=(0.7, 0.25), text_size=(500, 60), font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5), halign="right", valign="top")        
        
        self.add_widget(imgholder)
        self.add_widget(postTitle)
        self.add_widget(sponsoredLabel)

    def updateCanvas(self, *args):
        with self.canvas:
            self.background.pos = self.pos
            self.background.size = self.size
        
class postCell(FloatLayout):
    """Base layout for all post bodies"""
    
    def __init__(self, postid, title, voteCount, previousvote, img, source_url, timestamp, mediaType, caption, tint, *args, **kwargs):
        super(postCell, self).__init__(**kwargs)
        
        self.Title = title
        self.Caption = caption
        
        previousvote = int(previousvote)
        mediaType = int(mediaType)
        timeSincePost = int(time.time()) - int(timestamp)
        
        if tint == True:
            with self.canvas:
                Color(0.78823529411, 0.78823529411, 0.78823529411, 0.35)
                self.background = Rectangle(size=self.size, pos=self.pos)
        
            self.bind(pos=self.updateCanvas, size=self.updateCanvas)
        
        img.bind(on_press=lambda thumbbtn: Logger.info("flicknik: {} thumbnail pressed".format(postid)))
        
        if mediaType == 0:
            img.bind(on_press=lambda thumbphotoscrn: self.displayMedia(mediaType,source_url,postid))
        elif mediaType == 1:
            img.bind(on_press=lambda thumbphotoscrn: self.displayMedia(mediaType,source_url,postid))
        
        postTitle = Label(text=title, pos_hint={'center_x':0.5, 'top':0.7}, size_hint=(0.5, None), text_size=(dp(150), dp(75)), font_size="15sp", color=(0,0,0,1), halign="left", valign="top")
        
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
        
        upvote.bind(on_press=lambda upvt: vote(App.get_running_app().backend, App.get_running_app().usrid, postid, "upvote", "submission"))
        downvote.bind(on_press=lambda dnvt: vote(App.get_running_app().backend, App.get_running_app().usrid, postid, "downvote", "submission"))
        
        voteButtons.add_widget(upvote)
        voteButtons.add_widget(downvote)
        
        # Note: spaces are in the labelbuttons for spacing purposes
        buttonBar = BoxLayout(orientation="horizontal", pos_hint={'center_x':0.5, 'y':0.0175}, size_hint=(0.425, 0.15))
        reply = labelButton(text="Reply   ", font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5))
        reply.bind(on_press=lambda replyqueue: getReplyScreen(postid, title, voteCount, previousvote, img, source_url, timestamp, mediaType, caption))
        report = labelButton(text="Report", font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5))
        report.bind(on_press=lambda reportnotify: self.queuePopup("report", postid))
        block = labelButton(text=" Block", font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5))
        block.bind(on_press=lambda blocknotify: self.queuePopup("block", postid))
        hide = labelButton(text="  Hide", font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5))
        hide.bind(on_press=lambda hidenotify: self.queuePopup("hide", postid))
        
        buttonBar.add_widget(reply)
        buttonBar.add_widget(report)
        buttonBar.add_widget(hide)
        buttonBar.add_widget(block)

        imgholder = BoxLayout(orientation="horizontal", size_hint=(0.25, 1), pos_hint={'right':0.2625, 'top':1})
        imgholder.add_widget(img)
        
        timeSince = Label(text=formatTime(timeSincePost), pos_hint={'right':0.9825, 'top':0.9825}, size_hint=(0.7, 0.25), text_size=(dp(250), dp(35)), font_size="13sp", color=(0.11764705882352941, 0.4588235294117647, 0.8, 0.5), halign="right", valign="top")        
        
        self.add_widget(voteButtons)
        self.add_widget(buttonBar)
        self.add_widget(imgholder)
        self.add_widget(postTitle)
        self.add_widget(votes)
        self.add_widget(timeSince)
    
    def queuePopup(self, nType, postid):
        """Creates various popups ('report', 'block', 'hide') on the postcell body"""
        popup = notifyPopup(notificationType=nType, pid=postid, orientation="vertical", pos_hint={'center_x':0.5, 'center_y':0.5}, size_hint=(0.8, 0.8))
        self.add_widget(popup)
    
    def displayMedia(self, mediaType, source, postid):
        """Launches an intent to display media"""
        from jnius import cast
        from jnius import autoclass
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        
        playerintent = Intent()
        playerintent.setAction(Intent.ACTION_VIEW)
        if mediaType == 0:
            Logger.info('Video loaded! {}.mp4'.format(postid))
            playerintent.setDataAndType(Uri.parse(source), "image/*")
        elif mediaType == 1:
            Logger.info('Image loaded! {}.jpg'.format(postid))
            playerintent.setDataAndType(Uri.parse(source), "video/mp4")
        
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        currentActivity.startActivity(playerintent)
    
    def updateCanvas(self, *args):
        with self.canvas:
            self.background.pos = self.pos
            self.background.size = self.size
        
class homeScreen(Screen):
    """Base class for homeScreen"""
    
    order = 0
    
    processingPosts = False
    
    page = 1 # current page 
    postCount = 0 # the amount of posts on the page
    postsPerPage = 20 # the maximum amount of posts per page
    lowPost = 0 # the current lowest post on the page
    highPost = postsPerPage # the current highest post on the page
    
    def changePage(self, direction):
        """Updates post position loading limits"""
        if direction == 1 and self.postCount == self.postsPerPage:
            self.lowPost = self.highPost
            self.highPost += self.postsPerPage
            self.page += 1
            self.display(None, False)
        elif direction == -1 and self.page > 1:
            self.highPost = self.lowPost
            self.lowPost -= self.postsPerPage
            self.page -= 1
            self.display(None, False)
    
    def updatePageArrows(self):
        """Updates the back page/next page arrows based on what page the user is on and how many postCells there are"""
        if self.postCount == self.postsPerPage:
            self.ids.homescr_nextButton.source = "data/nextbutton.png"
        else:
            self.ids.homescr_nextButton.source = "data/blank.png"
    
        if self.page > 1:
            self.ids.homescr_backButton.source = "data/backbutton.png"
        else:
            self.ids.homescr_backButton.source = "data/blank.png"
    
    def overlayMessage(self, show, *args):
        """Initializes a message in the overlay, 0 - loading, 1 - blank, 2 - No posts, 3 - server unavailable"""
        if show == 0:
            self.ids.homescr_statusmsg.text = "Loading posts..."
        elif show == 1:
            self.ids.homescr_statusmsg.text = ""
        elif show == 2:
            self.ids.homescr_statusmsg.text = "No posts in your area, be the first!"
        elif show == 3:
            self.ids.homescr_statusmsg.text = "Server unavailable :("
    
    def buttonHighlight(self, btn):
        """Highlights the tab button of the current tab being displayed"""
        
        if btn == 0: # hot
            self.ids.homescr_hotsort.background_color = [0.14901960784, 0.57647058823, 1, 1]
            self.ids.homescr_newsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_topsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_badsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
        elif btn == 1: # top
            self.ids.homescr_hotsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_newsort.background_color = [0.14901960784, 0.57647058823, 1, 1]
            self.ids.homescr_topsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_badsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
        elif btn == 2: # new
            self.ids.homescr_hotsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_newsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_topsort.background_color = [0.14901960784, 0.57647058823, 1, 1]
            self.ids.homescr_badsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
        elif btn == 3: # bad
            self.ids.homescr_hotsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_newsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_topsort.background_color = [0.14901960784, 0.57647058823, 1, 0.5]
            self.ids.homescr_badsort.background_color = [0.14901960784, 0.57647058823, 1, 1]
    
    def processPosts(self, request, result, *args, **kwargs):
        """Processes data into postCells and puts them into homeScreen's ScrollView"""
        
        self.ids.homescr_output.clear_widgets()
        
        i = 0
        connectionError = False
        try:
            jsonResponse = json.loads(result)
            jsonData = jsonResponse["Data"]
            
            for post in jsonData:
                Title = post['Title']
                Caption = post['Caption']
                Location = post['Location']
                Votes = post['Votes']
                Userid = post['Userid']
                Postid = post['Postid']
                Timestamp = post['Timestamp']
                MediaType = post['MediaType']
                Previousvote = post['Previousvote']
                
                
                source_url = App.get_running_app().backend + Location
                if int(MediaType) == 0:
                    img = imageButton(source=App.get_running_app().backend + "uploads/{}/thumbnails/{}".format(Location.split('/')[1], Location.split('/')[2]))
                elif int(MediaType) == 1:
                    img = imageButtonLocal(source="data/videoplaceholder.png")
                    
                if i%2 == 0:
                    postFormat = postCell(Postid, Title, Votes, Previousvote, img, source_url, Timestamp, MediaType, Caption, True)
                else:
                    postFormat = postCell(Postid, Title, Votes, Previousvote, img, source_url, Timestamp, MediaType, Caption, False)
            
                self.ids.homescr_output.add_widget(postFormat)
                i += 1
                
                self.postCount = i
        
                self.updatePageArrows()
            self.ids.homescr_output.add_widget(FloatLayout())
            self.ids.homescr_output.add_widget(FloatLayout())
        except:
            self.overlayMessage(3)
            connectionError = True
        
        if connectionError == False:
            if i > 0:
                self.overlayMessage(1)
            else:
                self.overlayMessage(2)

    def display(self, Postorder=None, refreshPosts=True):
        """Initializes server querying and display process. Postorder is the post order setting, refreshPosts does full refresh (get coords then posts)"""
        
        self.ids.homescr_output.clear_widgets()
        
        self.overlayMessage(0)
        
        if Postorder == None: # if none don't change anything, just make sure the button is highlighted
            self.buttonHighlight(self.order)
        else: # if the order specification has changed, change homeScreen's order property and reset the page settings to the first page
            self.page = 1
            self.lowPost = 0
            self.highPost = self.postsPerPage
            self.order = Postorder
        
        if refreshPosts == True:
            Clock.schedule_once(lambda initializeRefresh: App.get_running_app().getCoordinates(), 0.1)
        else:
            if App.get_running_app().lat is not None and App.get_running_app().lon is not None:
                Clock.schedule_once(lambda initializePosts: self.getPosts(), 0.1)
            else:
                Clock.schedule_once(lambda initializeRefresh: App.get_running_app().getCoordinates(), 0.1)
        
    def getPosts(self):
        """Gets post data from the server and sends them to processPosts to be processed"""
        url = App.get_running_app().backend + "displayPosts.php"
        values = {"userid":App.get_running_app().usrid, "lat":App.get_running_app().lat, "long":App.get_running_app().lon, "displayMode":self.order, "lowPost":self.lowPost, "highPost":self.highPost}
        headers = {"Content-type" : "application/x-www-form-urlencoded"}
        data = urllib.urlencode(values)
        binary_data = data.encode('ascii')
        
        UrlRequest(url, req_body=binary_data, req_headers=headers, on_success=self.processPosts, on_failure=self.processPosts)
