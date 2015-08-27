#!/usr/bin/python
import sys

# pass in a string and where it came from, return the string to send, and the target

def response(event):
    final_message = "Message received."
    payload = {"target" : event.target, "message" : final_message}

    return payload

if __name__ == "__main__":
    class Event:
        def __init__(self, target, message):
            self.target = target
            self.message = message

    print("Debug Mode: Enter a message to parse. q = quit")

    while True:
        message = input('>>> ')
        event = Event(target = "self", message = message)
        if message == "q": break
        payload = response(event)
        print(payload['message'])

    sys.exit()