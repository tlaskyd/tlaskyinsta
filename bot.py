import os
import json
import random
import logging
from typing import *
from itertools import cycle
from instaloader import Post

from tlasky_insta.utils import post_url
from tlasky_insta import Notification, NotificationType
from tlasky_insta.bot import AbstractBot, run_bots, BotExitException

"""
This is a simple bot example. It is used to farm followers.
"""


class TlaskyBot(AbstractBot):
    def __init__(self, username: str, password: str, interests: List[Union[str, int]], **kwargs):
        super().__init__(username, password, **kwargs)
        self.insta.quiet = True

        self.interests_iterators = cycle([
            self.loader.get_location_posts(interest)
            if type(interest) == int else
            self.loader.get_hashtag_posts(interest)
            for interest in interests
        ])
        self.posts: Set[str] = set()
        self.last_notification: Union[None, Notification] = self.insta.get_notifications()[0]

        # Settings
        self.posts_file = f'./{username}_posts.json'
        self.insta.logger.setLevel(logging.INFO)
        self.min_posts = 10
        self.scheduler.every(1).minute.do(self.process_notifications)
        self.scheduler.every(20).to(30).minutes.do(self.like_post)

    def add_posts(self, iterable: Iterator[Post], n: int):
        added_posts = 0
        while added_posts < n:
            try:
                post = next(iterable)
                if not post.viewer_has_liked and post not in self.posts:
                    self.logger.info(f'Adding {post_url(post)} by {post.owner_username} ({len(self.posts)}+1)')
                    self.posts.add(post.shortcode)
                    added_posts += 1
            except StopIteration:
                self.logger.warning(f'There are no other posts for {iterable}')
                break

    def process_notifications(self):
        notifications = self.insta.get_notifications()
        for notification in notifications:
            if self.last_notification.at < notification.at:
                author = notification.get_user(self.context)
                media = notification.get_media(self.context)
                message = f'Notification {notification.type.name} by {author.username}'
                if media:
                    message += f' {post_url(media)}'
                self.logger.info(message)
                # Like comments and mentions
                if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                    for comment in notification.get_media(self.context).get_comments():
                        if comment.text == notification.text:
                            self.insta.like_comment(comment)
                # Add posts from notification author to posts to like
                if not author.followed_by_viewer:
                    self.add_posts(author.get_posts(), 2)
                # "Watch" authors story
                if author.has_viewable_story:
                    stories = list(self.loader.get_stories([author.userid]))[0]
                    for item in stories.get_items():
                        self.insta.seen_story(stories, item)
        if self.last_notification.at < notifications[0].at:
            self.last_notification = notifications[0]
        self.insta.mark_notifications()

    def like_post(self):
        shortcode = random.choice(list(self.posts))
        post = Post.from_shortcode(self.context, shortcode)
        self.logger.info(f'Liking {post_url(post)} by {post.owner_username} ({len(self.posts)})')
        if not self.insta.like_post(post).viewer_has_liked:
            self.logger.warning('Liking is probably banned, removing session file')
            os.remove(self.session_file)
            raise BotExitException()
        self.posts.remove(shortcode)

    def on_start(self):
        if os.path.isfile(self.posts_file):  # Load saved posts
            self.logger.info('Loading saved posts')
            with open(self.posts_file, 'r') as file:
                self.posts.update(json.load(file))

    def loop(self):
        while len(self.posts) < self.min_posts:  # Refilling posts
            self.add_posts(next(self.interests_iterators), 1)

    def on_exit(self):
        self.logger.info('Saving loaded posts')
        with open(self.posts_file, 'w') as file:  # Save loaded posts
            json.dump(
                list(self.posts), file,
                indent=4, sort_keys=True
            )


if __name__ == '__main__':
    from config import usernames_passwords, interests

    try:
        import coloredlogs

        coloredlogs.install()
    except ImportError:
        pass

    run_bots(*(
        TlaskyBot(username, password, interests)
        for username, password in usernames_passwords
    ))
