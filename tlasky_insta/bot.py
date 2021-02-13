import os
import time
from instaloader import Instaloader, InstaloaderException

from .insta import TlaskyInsta
from .utils import safe_login


class BotExitException(Exception):
    """
    Just rise it if you want to safely exit run_bots loop.
    """
    pass


class AbstractBot:
    def __init__(self, username: str, password: str, data_path: str = './'):
        self.session_file = os.path.join(data_path, f'{username}_session.pickle')
        self.posts_file = os.path.join(data_path, f'{username}_posts.pickle')

        self.loader = Instaloader()
        self.context = self.loader.context
        safe_login(self.loader, username, password, self.session_file)
        self.insta = TlaskyInsta(self.loader)

    def log(self, *args, **kwargs):
        print(self.context.username, '-', *args, **kwargs)

    def loop(self):
        pass

    def on_open(self):
        pass

    def on_close(self):
        pass


def run_bots(*bots: AbstractBot):
    try:
        for bot in bots:
            bot.on_open()
        while True:
            for bot in bots:
                try:
                    bot.loop()
                except InstaloaderException:
                    pass
            time.sleep(0.01)
    except (KeyboardInterrupt, BotExitException):
        pass
    finally:
        for bot in bots:
            bot.on_close()
