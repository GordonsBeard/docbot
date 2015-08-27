#!/usr/bin/python
"""This tests the YouTube"""

import unittest
import re

from ircutils3.events import MessageEvent

from youtube import YouTubeIdent, YouTubeSearch

class TestYouTubeSearch(unittest.TestCase):
    """ This is for  testing the YouTube search functionality. """

    user = "TestUser!testuser@test.com"
    channel = "#channel"

    prvmsg = "PRIVMSG"
    test_simple_query = "!yt 5 Stages of PSN Loss"
    valid_return = '\x02*** YouTube: \x02\x02\x1f5 Stages of PSN Loss\x1f\x02'

    def _clean_pretty(self, pretty):
        post_regex = ".\(post \d+\)"
        rx = re.compile(post_regex)
        rd = rx.search(pretty)
        if rd:
            cleaned = re.sub(rx, '', pretty)
            return cleaned
        else:
            return pretty

    def _build_message_event(self, message, user="TestUser!testuser@test.com", method="PRIVMSG", channel="#channel"):
        return MessageEvent(user, method, [channel, message])

    def test_valid_search(self):
        """ This search should return a valid, public, video. """
        valid_message_event = self._build_message_event(self.test_simple_query)
        ytsearch = YouTubeSearch(valid_message_event)
        cleaned = self._clean_pretty(ytsearch.pretty)
        self.assertEqual(cleaned, self.valid_return)

class TestYouTubeIdent(unittest.TestCase):
    """ This is for testing the core identify function in the YouTube module. """

    # Setup
    user = "TestUser!testuser@test.com"
    channel = "#channel"

    prvmsg = "PRIVMSG"
    notice = "NOTICE"

    post_regex = ".\(post \d+\)"
    rx = re.compile(post_regex)

    # Test Data
    valid_url = "http://www.youtube.com/watch?v=iVAWm8VNmQA"
    valid_message = "have you guys seen http://youtu.be/iVAWm8VNmQA?"
    valid_response = '\x02*** YouTube: \x02\x02\x1fA Tribute to the Snackish\x1f\x02'

    invalid_url = "http://youtu.be/i333AWm8VNmQA"
    invalid_message = "they named their pokemon some garbage like ch?v=iVAW"
    error_400 = "HTTP Error 400: Bad Request"

    deleted_url = "http://www.youtube.com/watch?v=k-rjwg_9mdw"
    private_url = "http://youtu.be/IC0C5w1-T1Y"

    def _clean_pretty(self, pretty):
        rd = self.rx.search(pretty)
        if rd:
            cleaned = re.sub(self.rx, '', pretty)
            return cleaned
        else:
            return pretty

    def _build_message_event(self, message, user="TestUser!testuser@test.com", method="PRIVMSG", channel="#channel"):
        return MessageEvent(user, method, [channel, message])

    # Messages
    def test_valid_url(self):
        """ This URL should pass with a valid response. """
        valid_message_event = self._build_message_event(self.valid_url)

        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(self._clean_pretty(ytident.pretty), self.valid_response)

    def test_valid_message(self):
        """ This message should pass with a valid response. """
        valid_message_event = self._build_message_event(self.valid_message)
        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(self._clean_pretty(ytident.pretty), self.valid_response)

    def test_invalid_url(self):
        """ Because this is an invalid URL, this should return an IndexError exception """
        valid_message_event = self._build_message_event(self.invalid_url)
        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(type(ytident.pretty), IndexError)

    def test_invalid_message(self):
        """ Because this is an invalid message, this should return an IndexError exception """
        valid_message_event = self._build_message_event(self.invalid_message)
        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(type(ytident.pretty), IndexError)

    def test_private_message_not_increasing_viewcount(self):
        """ With a valid URL given in a PM, we should not increase the counter. """
        valid_message_event = self._build_message_event(self.valid_url, channel=self.user)
        ytident1 = YouTubeIdent(valid_message_event)

        regex = ".\(post (\d+)\)"
        rx = re.compile(regex)
        rd = rx.search(ytident1.pretty)

        first_count = rd.groups()[0]

        ytident2 = YouTubeIdent(valid_message_event)

        regex = ".\(post (\d+)\)"
        rx = re.compile(regex)
        rd = rx.search(ytident1.pretty)

        second_count = rd.groups()[0]

        self.assertEqual(first_count, second_count)

    # Responses
    def test_deleted_video_url(self):
        """ Because this is a deleted video, this should return an IndexError exception """
        valid_message_event = self._build_message_event(self.deleted_url)
        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(type(ytident.pretty), IndexError)

    def test_private_video_url(self):
        """ Because this is a private video, this should return an IndexError exception """
        valid_message_event = self._build_message_event(self.private_url)
        ytident = YouTubeIdent(valid_message_event)
        self.assertEqual(type(ytident.pretty), IndexError)


def main():
    unittest.main()

if __name__ == "__main__":
    main()