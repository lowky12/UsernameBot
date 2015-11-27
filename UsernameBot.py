#!/usr/bin/env python2

import praw
import time
import settings
from prawoauth2 import PrawOAuth2Server, PrawOAuth2Mini
import UsernameManager

reddit_client = praw.Reddit(user_agent=settings.user_agent)
username_manager = UsernameManager.UsernameManager(reddit_client)
already_done = set()


def bot_init():
    oauthserver = PrawOAuth2Server(reddit_client, settings.reddit_app_key, settings.reddit_app_secret, state=settings.user_agent, scopes=settings.scopes)
    oauthserver.start()
    tokens = oauthserver.get_access_codes()
    print(tokens)
    write_config(tokens)


def write_config(tokens):
    settings = 'settings.py'
    replacements = {'{{access_token}}': tokens['access_token'], '{{refresh_token}}': tokens['refresh_token']}
    lines = []
    with open(settings) as infile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            lines.append(line)
    with open(settings, 'w') as outfile:
        for line in lines:
            outfile.write(line)


def compose(s, string, value):
    key = '{{' + string + '}}'
    if key in s:
        s.replace(key, value)
    return s


def bot_main():
    oauth_helper = PrawOAuth2Mini(reddit_client, app_key=settings.reddit_app_key, app_secret=settings.reddit_app_secret,
                                  access_token=settings.reddit_access_token, scopes=settings.scopes, refresh_token=settings.reddit_refresh_token)
    print 'UsernameBot Online!'
    while True:
        try:
            bot_logic(oauth_helper)
        except praw.errors.OAuthInvalidToken:
            oauth_helper.refresh()
        time.sleep(30)


def bot_logic(oauth_helper):
    oauth_helper.refresh()
    subreddit = reddit_client.get_subreddit(settings.subreddit)
    submissions = subreddit.get_new(limit=100)
    for submission in submissions:
        if isinstance(submission, praw.objects.Submission):
            if submission.id not in already_done:
                bot_process_post(subreddit, submission)


def bot_process_post(subreddit, submission):
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
    already_done.add(submission.id)


def check_username_posts(subreddit, submission):
    username = submission.title
    if not username_manager.valid_username(username):
        if len(username) > 20:
            print '-- removed due to name length'
        else:
            print '-- invalid username'

        submission.remove(False)
    else:
        if username_manager.user_exists(username):
            print '-- tagged as taken'
            reddit_client.set_flair(subreddit, submission, flair_text='TAKEN')

if __name__ == '__main__':
    if settings.reddit_access_token == '{{access_token}}':
        bot_init()
    else:
        bot_main()