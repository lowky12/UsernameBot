#!/usr/bin/env python2
"""
Bot Core Functionality
"""

import praw
import time
import settings
from prawoauth2 import PrawOAuth2Server, PrawOAuth2Mini
import UsernameManager

USER_AGENT = 'python:UsernameMod:v1.2 (by /u/lowky12)'

REDDIT_CLIENT = praw.Reddit(user_agent=USER_AGENT)
USERNAME_MANAGER = UsernameManager.UsernameManager(REDDIT_CLIENT)
ALREADY_DONE = set()


def bot_init():
    """
    Initialises the bot setting the refresh_token and the refresh_token through oauth
    """
    oauth_server = PrawOAuth2Server(REDDIT_CLIENT,
                                    settings.reddit_app_key, settings.reddit_app_secret,
                                    state=USER_AGENT, scopes=settings.scopes)
    oauth_server.start()
    tokens = oauth_server.get_access_codes()
    print tokens
    write_config(tokens)


def write_config(tokens):
    """
    Writes the tokens to the settings file
    :param tokens:
    """
    settings_file = 'settings.py'
    replacements = {
        '{{access_token}}': tokens['access_token'],
        '{{refresh_token}}': tokens['refresh_token']
    }
    lines = []
    with open(settings_file) as infile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            lines.append(line)
    with open(settings_file, 'w') as outfile:
        for line in lines:
            outfile.write(line)


def compose(string, key, value):
    """
    Takes string and replaces the template key with value
    :param string:
    :param key:
    :param value:
    :return String:
    """
    key = '{{' + key + '}}'
    if key in string:
        string.replace(key, value)
    return string


def bot_main():
    """
    Main function of the bot. Contains logic loop and oauth
    """
    oauth_helper = PrawOAuth2Mini(REDDIT_CLIENT,
                                  app_key=settings.reddit_app_key,
                                  app_secret=settings.reddit_app_secret,
                                  access_token=settings.reddit_access_token,
                                  scopes=settings.scopes,
                                  refresh_token=settings.reddit_refresh_token)
    print 'UsernameBot Online!'
    while True:
        try:
            bot_logic(oauth_helper)
        except praw.errors.OAuthInvalidToken:
            oauth_helper.refresh()
        time.sleep(30)


def bot_logic(oauth_helper):
    """
    Logic function of the bot gets new submissions and possesses them
    :param oauth_helper:
    """
    oauth_helper.refresh()
    subreddit = REDDIT_CLIENT.get_subreddit(settings.subreddit)
    submissions = subreddit.get_new(limit=100)
    for submission in submissions:
        if isinstance(submission, praw.objects.Submission):
            if submission.id not in ALREADY_DONE:
                bot_process_post(subreddit, submission)


def bot_process_post(subreddit, submission):
    """
    Submissions that are not already done are possessed here
    :param subreddit:
    :param submission:
    """
    username = submission.title
    print 'Possessing %s (ID:%s):' % (username, submission.id)
    if False:  # submission.get_sticky():
        print '-- skipping due to importance'
    else:
        if submission.get_flair_choices()['current']['flair_text'] == "DISCUSSION":
            print '-- skipping due to flair'
        else:
            check_username_posts(subreddit, submission)
    print '-- done!\n'
    ALREADY_DONE.add(submission.id)


def check_username_posts(subreddit, submission):
    """
    Submissions that are not skipped are then checked and dealt with accordingly
    :param subreddit:
    :param submission:
    """
    username = submission.title
    if not USERNAME_MANAGER.valid_username(username):
        if len(username) > 20:
            print '-- removed due to name length'
        else:
            print '-- invalid username'

        submission.remove(False)
    else:
        if USERNAME_MANAGER.user_exists(username):
            print '-- tagged as taken'
            REDDIT_CLIENT.set_flair(subreddit, submission, flair_text='TAKEN')

# Main Function
if __name__ == '__main__':
    if settings.reddit_access_token == '{{access_token}}':
        bot_init()
    else:
        bot_main()
