__author__ = 'Lachlan'

from praw import errors
import re


class UsernameManager:
    user_pattern = re.compile("\A([0-9a-zA-Z])+\Z")

    def __init__(self, reddit_client):
        self.reddit_client = reddit_client

    def user_exists(self, username):
        try:
            self.reddit_client.get_redditor(username, fetch=True)
            return True
        except errors.NotFound:
            return False

    def valid_username(self, username):
        if len(username) < 3 or len(username) > 20:
            return False
        if not re.match(self.user_pattern, username):
            return False
        return True
