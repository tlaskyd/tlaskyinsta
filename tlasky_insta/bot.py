import os
import time
from schedule import Scheduler
from instaloader import Instaloader, InstaloaderException

from .utils import safe_login
from .insta import TlaskyInsta


class BotExitException(Exception):
    """
    Just rise it if you want to safely exit run_bots loop.
    """
    pass


class AbstractBot:
    def __init__(self, username: str, password: str, **kwargs):
        self.session_file = kwargs.get('session_path', f'./{username}_session.pickle')

        self.loader = Instaloader()
        self.context = self.loader.context
        safe_login(self.loader, username, password, self.session_file)
        self.insta = TlaskyInsta(self.loader)
        self.logger = self.insta.logger
        self.scheduler = Scheduler()

    def on_start(self):
        """
        Here you can load your stuff.
        """
        pass

    def loop(self):
        """
        Main bot function.
        """

    def on_exit(self):
        """
        Here you can save your stuff.
        """
        self.loader.save_session_to_file(self.session_file)


def run_bots(*bots: AbstractBot, min_delay: float = 1):
    """
    This function will run any bots.
    """
    for bot in bots:
        bot.on_start()
    try:
        while True:
            start = time.time()
            for bot in bots:
                try:
                    bot.loop()
                    bot.scheduler.run_pending()
                except InstaloaderException:
                    pass
            delay = min(
                min(bot.scheduler.idle_seconds for bot in bots),  # Scheduler delay
                min_delay - (time.time() - start)  # Loop delay
            )
            if delay > 0:
                time.sleep(delay)
    except (KeyboardInterrupt, BotExitException):
        pass
    finally:
        for bot in bots:
            bot.on_exit()
