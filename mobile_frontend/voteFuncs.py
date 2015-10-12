import urllib
import urllib2
import json

from kivy.network.urlrequest import UrlRequest

from kivy.logger import Logger

def vote(backendUrl, usrid, postid, vote, postType, *args):
    """Sends user vote to server for posts and replies"""
    
    Logger.info("submitting {} vote for {}".format(vote, postid))
    
    url = backendUrl + "vote.php"
    
    values = {"userid":usrid, "id":postid, "voteType":vote, "postType":postType}
        
    headers = {"Content-type" : "application/x-www-form-urlencoded"}
    data = urllib.urlencode(values)
    binary_data = data.encode('ascii')
    req = UrlRequest(url, req_body=binary_data, req_headers=headers)

def updateVoteDisplay(upvt, dnvt, countLabel, voteCount, vote):
    """Updates UI vote buttons and vote count in postCells and replyCells"""

    if vote > 0 and upvt.source == "data/up_unclicked.png":
        upvt.source = "data/up_clicked.png"
        dnvt.source = "data/down_unclicked.png"
        countLabel.text = str(int(voteCount) + int(vote))
        
    elif vote < 0 and dnvt.source == "data/down_unclicked.png":
        upvt.source = "data/up_unclicked.png"
        dnvt.source = "data/down_clicked.png"
        countLabel.text = str(int(voteCount) + int(vote))
    
    elif vote == 0:
        countLabel.text = voteCount
        if upvt.source == "data/up_unclicked.png":
            upvt.source = "data/up_clicked.png"
            dnvt.source = "data/down_unclicked.png"
        elif dnvt.source == "data/down_unclicked.png":
            upvt.source = "data/up_unclicked.png"
            dnvt.source = "data/down_clicked.png"
    
    upvt.reload()
    dnvt.reload()
