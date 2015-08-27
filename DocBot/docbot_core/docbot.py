#!/usr/bin/python

# Setup and connect the bot to the server, pass along strings to docbot_core

from ircutils3 import bot
from docbot_core import response

# Settings
BOT_NAME = "DR"
NETWORK = "irc.gamesurge.net"
CHANNELS = ["#thefuture",]

class DocBot(bot.SimpleBot):
    def on_welcome(self, event):
        for chan in CHANNELS:
            self.join(chan)

    def on_join(self, event):
        pass
    
    def on_message(self, event):
        payload = response(event)
        if payload['message'] != "":
            self.send_message(event.target, payload['message'])

if __name__ == "__main__":
    docbot = DocBot(BOT_NAME)
    docbot.connect(NETWORK)
    docbot.start()