import os
import time
from instaloader import Instaloader, InstaloaderException

from .utils import safe_login
from .insta import TlaskyInsta


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
        """
        Just print / logging delegate.
        """
        print(self.context.username, '-', *args, **kwargs)

    def loop(self):
        """
        Main bot function.
        """
        pass

    def on_start(self):
        """
        Here you can load your stuff.
        """
        pass

    def on_exit(self):
        """
        Here you can save your stuff.
        """
        pass


def run_bots(*bots: AbstractBot):
    """
    This function will run any bots.
    """
    try:
        for bot in bots:
            bot.on_start()
        while True:  # Loop all bots max once per seconds (Don't waist all cpu just for looping.)
            start = time.time()
            for bot in bots:
                try:
                    bot.loop()
                except InstaloaderException:
                    pass
            took = time.time() - start
            if took < 1:
                time.sleep(1 - took)
    except (KeyboardInterrupt, BotExitException):
        pass
    finally:
        for bot in bots:
            bot.on_exit()
