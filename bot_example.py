import os
from typing import *
from tlaskyinsta import *
from instaloader import *
from datetime import datetime
from random import uniform, choices

try:
    from credentials import username, password, session_filepath
except ImportError:
    from credentials_example import username, password, session_filepath

loader = Instaloader()
insta = TlaskyInsta(loader)

"""
OR
insta = TlaskyInsta()
loader = insta.loader
"""

if os.path.isfile(session_filepath):
    # Loading session using Instaloader does not work for me (Some linux bs.), so I made this.
    insta.load_session(session_filepath)
else:
    loader.login(username, password)
    insta.save_session(session_filepath)

assert loader.test_login(), 'Bad session or credentials.'

tags = 'czechgirl slovakgirl czechwomen slovakwomen nature czechnature slovaknature'.split()
locations = [
    213586561,  # HK
    215268388  # PCE
]
like_comments = True
follow_back = False

while True:
    try:
        # React to notifications
        last_notification_at: Union[None, datetime] = None
        for notification in insta.notifications():
            # datetime.datetime compare
            if last_notification_at and last_notification_at > notification.at:
                break
            last_notification_at = notification.at
            if like_comments and notification.type is NotificationType.COMMENT:
                print('Liking comment:', notification.media)
                insta.like_comment(notification.media)
                wait(minutes(uniform(10, 15)))
            elif follow_back and notification.type is NotificationType.STARTED_FOLLOWING:
                print('Following back:', notification.media)
                insta.follow(notification.media)
                wait(minutes(uniform(10, 15)))

        # Like posts
        posts: Set[Post] = set()
        for tag in tags:
            print('Loading posts for hashtag:', tag)
            tag_posts = gen_to_list(loader.get_hashtag_posts(tag), 50)
            posts.update(choices(tag_posts, k=20))
        wait(minutes(uniform(1, 5)))
        for loc in locations:
            print('Loading posts for location:', loc)
            loc_posts = gen_to_list(loader.get_location_posts(str(loc)), 50)
            posts.update(choices(loc_posts, k=20))
        wait(minutes(uniform(1, 5)))
        for i, post in enumerate(posts):
            if not post.viewer_has_liked:
                print(f'Liking post [{i + 1}/{len(posts)}]:', post)
                insta.like_post(post)
                wait(minutes(uniform(10, 15)))
        wait(hours(uniform(1 / 4, 1 / 2)))
    except KeyboardInterrupt:
        insta.save_session(session_filepath)
        break
