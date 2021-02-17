from instaloader import Instaloader
from tlasky_insta import TlaskyInsta
from tlasky_insta.utils import safe_login

from config import usernames_passwords

loader = Instaloader()
safe_login(
    loader,
    *usernames_passwords[0],
    './david_tlaskal_session.pickle'
)
insta = TlaskyInsta(loader)

last_notification = None
while True:
    notifications = insta.get_notifications()
    if not last_notification:
        last_notification = notifications[0]
        continue
    for notification in notifications:
        if last_notification.at < notification.at:
            print(notification)
    if last_notification.at < notifications[0].at:
        last_notification = notifications[0]
    insta.mark_notifications()
