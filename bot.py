import os
import json
import time
import logging
from typing import *
from random import uniform
from itertools import cycle
from instaloader import Post, RateController

from tlasky_insta.utils import post_url
from tlasky_insta import Notification, NotificationType
from tlasky_insta.bot import BaseBot, run_bots, BotExitException

"""
This is a simple bot example. It is used to farm followers.
"""


class TlaskyRateController(RateController):
    def wait_before_query(self, query_type: str) -> None:
        pass

    def handle_429(self, query_type: str) -> None:
        delay = uniform(60 * 30, 60 * 60)
        print(f'Too many requests! Sleeping for {round(delay, 2)}s, then exit.')
        time.sleep(delay)
        raise BotExitException('Too many requests, exiting...')


class TlaskyBot(BaseBot):
    def __init__(self, username: str, password: str, interests: List[Union[str, int]], **kwargs):
        super().__init__(
            username, password,
            loader_kwargs=dict(rate_controller=TlaskyRateController),
            **kwargs
        )
        self.insta.quiet = True

        self.interests_iterators = cycle([
            self.loader.get_location_posts(interest)
            if type(interest) == int else
            self.loader.get_hashtag_posts(interest)
            for interest in interests
        ])
        self.posts: List[str] = list()
        self.last_notification: Union[None, Notification] = self.insta.get_notifications()[0]

        # Settings
        self.posts_file = f'./{username}_posts.json'
        self.insta.logger.setLevel(logging.INFO)
        self.min_posts = 10
        self.scheduler.every(5).minutes.do(self.process_notifications)
        self.scheduler.every(30).to(45).minutes.do(self.like_post)

    def add_posts(self, iterable: Iterator[Post], count: int = 1, index: int = -1):
        added_posts = 0
        while added_posts < count:
            try:
                post = next(iterable)
                if not post.viewer_has_liked and post.shortcode not in self.posts:
                    self.logger.info(f'Adding {post_url(post)} by {post.owner_username} ({len(self.posts)}+1)')
                    self.posts.insert(index, post.shortcode)
                    added_posts += 1
            except StopIteration:
                self.logger.warning(f'There are no other posts or it\'s a private profile.')
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
                            self.logger.info(f'Liking comment by {author.username} at {post_url(media)}')
                            self.insta.like_comment(comment)
                # Add posts from notification author to posts to like
                if not author.followed_by_viewer and not author.is_private:
                    self.add_posts(author.get_posts(), count=2, index=0)
                # "Watch" authors story
                if author.has_viewable_story:
                    self.logger.info(f'Watching story by {author.username}')
                    stories = list(self.loader.get_stories([author.userid]))[0]
                    for item in stories.get_items():
                        self.insta.seen_story(stories, item)
        if self.last_notification.at < notifications[0].at:
            self.last_notification = notifications[0]
        self.insta.mark_notifications()

    def like_post(self):
        shortcode = list(self.posts).pop(0)
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
                self.posts = list({
                    *self.posts,
                    *json.load(file)
                })

    def loop(self):
        if len(self.posts) < self.min_posts:  # Refilling posts
            self.add_posts(next(self.interests_iterators), 1)

    def on_exit(self):
        self.logger.info('Saving loaded posts')
        with open(self.posts_file, 'w') as file:  # Save loaded posts
            json.dump(
                self.posts, file,
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
