#!/usr/bin/python
"""
This is the YouTube identify module.
Features:
    - YouTubeIdent
        * log = True, set to False for PMs?
        - get_videoinfo():  Does the string building of the pretty output.
        - log_video():      Logs +1 view for the video in a sqlite3 db.
"""

from oauth2client.tools import argparser
import datetime, os, re, sqlite3
from urllib.error import HTTPError
from urllib.request import urlopen
from ircutils3 import format
from ircutils3.events import MessageEvent
import requests

# Settings
DB_FILENAME = "videos.db"

# Check for database.
db_is_new = not os.path.exists(DB_FILENAME)

conn = sqlite3.connect(DB_FILENAME)

if db_is_new:

    cursor = conn.cursor()
    cursor.execute('''
    create table videos (
        id integer primary key autoincrement,
        vidid string unique not null,
        posts integer not null,
        firstdate datetime not null,
        firstsource string not null,
        firsttarget string not null,
        lastdate datetime not null,
        lastsource string not null,
        lasttarget string not null
    )''')

    try:
        conn.commit()
    except (sqlite3.Error):
        print("Error creating database.")

conn.close()

print("YouTube module loaded.")

# YouTube URL parser/identifier.
class YouTubeIdent:
    """ Class for containg the YouTube message and it's chat-friendly translation. """

    # Magic regex to pull out youtu.be/<vidid> or youtube.com/v?=<vidid>
    regex = re.compile("(?<=v(\=|\/))(?P<vid1>[-a-zA-Z0-9_]+)|(?<=youtu\.be\/)(?P<vid2>[-a-zA-Z0-9_]+)")


    def __init__(self, event):
        self.message = event.message
        self.source = event.source
        self.target = event.target

        rx = re.compile(self.regex)
        rd = rx.search(self.message)
        rd = rd.groupdict()
        self.vidid = rd['vid1'] if rd['vid1'] else rd['vid2']

        self.log = True if event.target[0] == "#" else False

        self.pretty = self.get_videoinfo()


    def get_videoinfo(self):
        """ Returns a pretty string that in turn is used in YouTubeIdent.pretty """
        
        vidInfo = {}

        url = "https://www.googleapis.com/youtube/v3/videos?id={0}&key=AIzaSyC8bdcRUA3lBWQ4hxIESzbsyMgf0ABtdgI&fields=items(id,snippet(channelId,title,categoryId),statistics)&part=snippet,statistics".format(self.vidid)
        r = requests.get(url)
        js = r.json()

        try:
            vidInfo['title'] = js["items"][0]['snippet']['title']
        except IndexError as e:
            return e


        # Build the string.
        youtubeprefix = format.bold("*** YouTube: ")
        videotitle = format.underline(vidInfo['title'])
        videotitle = format.bold(videotitle)
        reposts = self.get_view_count(self.log)
        repoststring = format.filter(' (post {0})'.format(reposts)) if reposts > 1 else ''
        videoinfo = youtubeprefix + videotitle + repoststring

        return videoinfo

    def get_view_count(self, log):
        """ Take the video, give it +1 posts or stuff it into the database forever.
            Returns the number of posts the video has. """
        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.cursor()

        cursor.execute("SELECT posts from videos WHERE vidid = ?", (self.vidid,))
        data = cursor.fetchone()

        if data and log is False:
            return data[0]

        elif data is not None:
            posts = data[0] + 1
            cursor.execute("UPDATE videos SET posts = posts + 1 WHERE vidid = ?", (self.vidid,))

        else:
            posts = 1
            cursor.execute("INSERT INTO videos (vidid, posts, firstdate, firstsource, firsttarget, lastdate, lastsource, lasttarget) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (self.vidid, 1, datetime.datetime.now(), self.source, self.target, datetime.datetime.now(), self.source, self.target))

        conn.commit()
        conn.close()
        return posts



# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyC8bdcRUA3lBWQ4hxIESzbsyMgf0ABtdgI'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class YouTubeSearch:
    """ Class for containing the YouTube search result. """

    # Magic regex to get the query out of the !yt <query> message.
    regex = re.compile("((!yt) (?P<query>\"?.*\"?|\w+))")

    def __init__(self, event):
        self.message = event.message
        self.source = event.source
        self.target = event.target

        rx = re.compile(self.regex)
        rd = rx.search(self.message)
        rd = rd.groupdict()
        self.query = rd['query']

        try:
            self.pretty = self.youtube_search(event, self.query) 
        except HttpError as e:
            self.pretty = None

    def youtube_search(self, event, query):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=5
        ).execute()

        videos = []

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.


        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                vidid = search_result['id']['videoId']               
                fake_event = MessageEvent("self", "PRVMSG", ["self", "http://youtu.be/{0}".format(vidid)])
                pretty_ident = YouTubeIdent(fake_event)

                return pretty_ident.pretty