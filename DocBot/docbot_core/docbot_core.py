#!/usr/bin/python

# pass in a string and where it came from, return the string to send, and the target

import sys, re
from youtube import YouTubeIdent

commands = [ 
    YouTubeIdent,
            ]

regexes = [rx.regex for rx in commands] if commands is not 0 else None

def response(event):
    final_message = ""
    for i, rx in enumerate(regexes):
        if re.search(rx, event.message):
            final_message = commands[i](event)
            print(final_message.pretty)

    payload = {"target" : event.target, "message" : final_message}

    return payload

if __name__ == "__main__":
    class Event:
        def __init__(self, source, target, message):
            self.target = target
            self.source = source
            self.message = message

    print("Debug Mode: Enter a message to parse. q = quit")

    while True:
        message = input('>>> ')
        event = Event(target = "self", source = "self", message = message)
        if message == "q": break
        payload = response(event)
        print(payload['message'])

    sys.exit()