import os
import random
import pickle
import logging
from typing import *
from itertools import cycle
from instaloader import Post

from tlasky_insta.utils import post_url
from tlasky_insta import NotificationType
from tlasky_insta.bot import AbstractBot, run_bots, BotExitException

"""
This is a simple bot example. It is used to farm followers. 
"""


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

        # Settings
        self.insta.logger.setLevel(logging.INFO)
        self.min_posts = 10
        self.scheduler.every(2).minutes.do(self._notifications)
        self.scheduler.every(15).to(20).minutes.do(self._like_post)

    def __add_posts(self, iterable: Iterator[Post], n: int):
        added_posts = 0
        while added_posts < n:
            post = next(iterable)
            if not post.viewer_has_liked and post not in self.posts:
                self.logger.info(
                    f'Adding {post_url(post)} '
                    f'by {post.owner_username} '
                    f'({len(self.posts)} | {self.min_posts})'
                )
                self.posts.add(post)
                added_posts += 1

    def _notifications(self):
        for notification in self.insta.get_notifications():
            if self.insta.last_notifications_at < notification.at:
                author = notification.get_user(self.context)
                self.logger.info(
                    f'Notification {NotificationType.name} '
                    f'by {author.username} '
                    f'{post_url(notification.get_media(self.context))}'
                )
                # Like comments and mentions
                if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                    for comment in notification.get_media(self.context).get_comments():
                        if comment.text == notification.text:
                            self.insta.like_comment(comment)
                # Add 5 posts from notification author to posts to like
                if not author.followed_by_viewer:
                    self.__add_posts(author.get_posts(), 5)
                # "Watch" authors story
                if author.has_viewable_story:
                    stories = list(self.loader.get_stories([author.userid]))[0]
                    for item in stories.get_items():
                        self.insta.seen_story(stories, item)
        self.insta.mark_notifications()

    def _load_posts(self):
        while len(self.posts) <= self.min_posts:
            self.__add_posts(next(self.interests_iterators), 1)

    def _like_post(self):
        post = random.choice(list(self.posts))
        self.logger.info(
            f'Liking {post_url(post)} '
            f'by {post.owner_username}'
        )
        if not self.insta.like_post(post).viewer_has_liked:
            self.logger.warning('Liking is probably banned, removing session file')
            os.remove(self.session_file)
            raise BotExitException()
        self.posts.remove(post)

    def loop(self):
        self._load_posts()
        super().loop()

    def on_start(self):
        if os.path.isfile(self.posts_file):  # Load saved posts
            self.logger.info('Loading saved posts')
            with open(self.posts_file, 'rb') as file:
                self.posts = pickle.load(file)

    def on_exit(self):
        self.logger.info('Saving loaded posts')
        with open(self.posts_file, 'wb') as file:  # Save loaded posts
            pickle.dump(self.posts, file)


if __name__ == '__main__':
    from config import usernames_passwords, interests

    bots = {  # Create dict for future management
        username: TlaskyBot(username, password, interests)
        for username, password in usernames_passwords
    }
    run_bots(*bots.values())
