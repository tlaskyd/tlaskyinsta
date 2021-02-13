import os
import time
import random
import pickle
import shutil
import traceback
from typing import *
from instaloader import Instaloader, Post
from tlasky_insta.utils import safe_login, post_url
from tlasky_insta import TlaskyInsta, NotificationType


class ExitException(Exception):
    pass


def run_bots(*bots: 'TlaskyBot'):
    try:
        for bot in bots:
            bot.on_open()
        while True:
            for bot in bots:
                bot.loop()
            time.sleep(0.01)
    except (KeyboardInterrupt, ExitException):
        pass
    except Exception:
        traceback.print_exc()
    finally:
        for bot in bots:
            bot.on_close()


class TlaskyBot:
    def __init__(self, username: str, password: str, interests: List[Union[str, int]]):
        self.session_file = f'./{username}.pickle'
        self.posts_file = f'./{username}_posts.pickle'

        self.loader = Instaloader()
        self.context = self.loader.context
        safe_login(self.loader, username, password, self.session_file)
        self.insta = TlaskyInsta(self.loader)
        self.insta.log = self.log

        self.interests = interests

        self.min_posts = 10
        self.posts: Set[Post] = set()
        self.last_like_at = 0

    def log(self, *args, **kwargs):
        print(self.context.username, '-', *args, **kwargs)

    def __add_posts(self, iterable: Iterable[Post], n: int = 5):
        added_posts = 0
        for post in iterable:
            if not post.viewer_has_liked and post not in self.posts:
                self.log(
                    'Adding', post_url(post),
                    'by', post.owner_username,
                    f'({len(self.posts)} | {self.min_posts})'
                )
                self.posts.add(post)
                added_posts += 1
            if added_posts >= n:
                break

    def _notifications(self):
        if not self.insta.last_notifications_at or time.time() - self.insta.last_notifications_at.timestamp() > 60 * 2:
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
                        self.__add_posts(user.get_posts())
            self.insta.mark_notifications()

    def _load_posts(self):
        while len(self.posts) < self.min_posts:  # Have prepared at least 20 posts
            for item in self.interests:
                self.__add_posts(
                    self.loader.get_location_posts(item)
                    if type(item) == int else
                    self.loader.get_hashtag_posts(item)
                )

    def _like_post(self):
        if not self.last_like_at or time.time() - self.last_like_at > 60 * 15:  # Like random post every 15 minutes
            post = random.choice(list(self.posts))
            self.posts.remove(post)
            self.log(
                'Liking', post_url(post),
                'by', post.owner_username
            )
            if not self.insta.like_post(post).viewer_has_liked:
                self.log('Liking is probably banned, removing session file')
                shutil.rmtree(self.session_file)
                raise ExitException()
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
        with open(self.posts_file, 'wb') as file:  # Save loaded posts
            self.log('Saving loaded posts')
            pickle.dump(self.posts, file)


if __name__ == '__main__':
    from config import username, password

    bot = TlaskyBot(
        username, password,
        [
            244516490,  # CZ
            261698127,  # SK
            108100019211318,  # DE
            *'nature czechnature czechgirl slovaknature slovakgirl'.split()
        ]
    )
    # This way you can run bots for multiple users
    run_bots(bot)
