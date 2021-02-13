import os
import time
import random
import pickle
import shutil
from typing import *
from itertools import cycle
from instaloader import Post

from tlasky_insta.utils import post_url
from tlasky_insta import NotificationType
from tlasky_insta.bot import AbstractBot, run_bots, BotExitException


class TlaskyBot(AbstractBot):
    def __init__(self, username: str, password: str, interests: List[Union[str, int]]):
        super().__init__(username, password)

        self.insta.quiet = True

        self.interests_iterators = cycle([
            self.loader.get_location_posts(interest)
            if type(interest) == int else
            self.loader.get_hashtag_posts(interest)
            for interest in interests
        ])

        self.posts: Set[Post] = set()
        self.last_like_at = 0

        # Settings
        self.min_posts = 10
        self.notifications_delay = 60 * 2
        self.post_delay = 60 * 15

    def __add_posts(self, iterable: Iterator[Post], n: int):
        added_posts = 0
        while added_posts < n:
            post = next(iterable)
            if not post.viewer_has_liked and post not in self.posts:
                self.log(
                    'Adding', post_url(post),
                    'by', post.owner_username,
                    f'({len(self.posts)} | {self.min_posts})'
                )
                self.posts.add(post)
                added_posts += 1

    def _notifications(self):
        if not self.insta.last_notifications_at or \
                time.time() - self.insta.last_notifications_at.timestamp() > self.notifications_delay:
            for notification in self.insta.get_notifications():
                if self.insta.last_notifications_at < notification.at:
                    # Process comments and comments mentions
                    self.log(
                        'Notification', NotificationType.name,
                        'by', notification.get_user(self.context).username,
                        post_url(notification.get_media(self.context))
                    )
                    # Like comments and mentions
                    if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                        post = notification.get_media(self.context)
                        for comment in post.get_comments():
                            if comment.text == notification.text:
                                self.insta.like_comment(comment)
                    # Add 5 posts from notification author to posts to like.
                    user = notification.get_user(self.context)
                    if not user.followed_by_viewer:
                        self.__add_posts(user.get_posts(), 5)
            self.insta.mark_notifications()

    def _load_posts(self):
        while len(self.posts) <= self.min_posts:
            self.__add_posts(next(self.interests_iterators), 1)

    def _like_post(self):
        if not self.last_like_at or \
                time.time() - self.last_like_at > self.post_delay:  # Like random post every 15 minutes
            post = random.choice(list(self.posts))
            self.posts.remove(post)
            self.log(
                'Liking', post_url(post),
                'by', post.owner_username
            )
            if not self.insta.like_post(post).viewer_has_liked:
                self.log('Liking is probably banned, removing session file')
                shutil.rmtree(self.session_file)
                raise BotExitException()
            self.last_like_at = time.time()

    def loop(self):
        self._notifications()
        self._load_posts()
        self._like_post()

    def on_open(self):
        if os.path.isfile(self.posts_file):  # Load saved posts
            self.log('Loading saved posts')
            with open(self.posts_file, 'rb') as file:
                self.posts = pickle.load(file)

    def on_close(self):
        self.log('Saving loaded posts')
        with open(self.posts_file, 'wb') as file:  # Save loaded posts
            pickle.dump(self.posts, file)


if __name__ == '__main__':
    from config import usernames_passwords

    interests = [
        244516490,  # CZ
        261698127,  # SK
        108100019211318,  # DE
        'nature',  # Hashtags
        'czechnature',
        'czechgirl',
        'slovaknature',
        'slovakgirl'
    ]

    bots = {
        username: TlaskyBot(username, password, interests)
        for username, password in usernames_passwords
    }
    run_bots(*bots.values())
