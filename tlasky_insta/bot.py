import os
import time
import logging
from datetime import timedelta
from schedule import Scheduler
from humanize import naturaldelta
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
        self.logger = self.insta.logger
        self.scheduler = Scheduler()

    def loop(self):
        """
        Main bot function.
        """
        self.scheduler.run_pending()

    def on_start(self):
        """
        Here you can load your stuff.
        """
        pass

    def on_exit(self):
        """
        Here you can save your stuff.
        """
        self.loader.save_session_to_file(self.session_file)


def run_bots(*bots: AbstractBot):
    """
    This function will run any bots.
    """
    try:
        for bot in bots:
            bot.on_start()
        while True:
            delay = min([  # Don't waist all cpu just for looping.
                bot.scheduler.idle_seconds
                for bot in bots
            ])
            if delay > 0:
                logging.info(f'Sleeping for {naturaldelta(timedelta(seconds=delay))}.')
                time.sleep(delay)
            for bot in bots:
                try:
                    bot.loop()
                except InstaloaderException:
                    pass
    except (KeyboardInterrupt, BotExitException):
        pass
    finally:
        for bot in bots:
            bot.on_exit()
