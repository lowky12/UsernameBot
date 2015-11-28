#!/usr/bin/env python2
"""
Performs various operations on reddit usernames
"""

import re

from praw import errors


class UsernameManager(object):
    """
    Performs various operations on reddit usernames
    :param reddit_client:
    """
    user_pattern = re.compile(r"\A([0-9a-zA-Z])+\Z")

    def __init__(self, reddit_client):
        self.reddit_client = reddit_client

    def user_exists(self, username):
        """
        Checks if the user exists
        :param username:
        :return user exists:
        """
        try:
            self.reddit_client.get_redditor(username, fetch=True)
            return True
        except errors.NotFound:
            return False

    def valid_username(self, username):
        """
        Checks if the username is valid
        :param username:
        :return valid:
        """
        if len(username) < 3 or len(username) > 20:
            return False
        if not re.match(self.user_pattern, username):
            return False
        return True
