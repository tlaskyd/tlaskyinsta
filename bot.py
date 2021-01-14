import os
import random
from config import *
from tlasky_insta import *
from traceback import print_exc
from datetime import datetime, timedelta

loader = Instaloader()
if os.path.exists(session_path):
    loader.load_session_from_file(username, session_path)
else:
    loader.login(username, password)
loader.save_session_to_file(session_path)

insta = TlaskyInsta(loader)

# Follow tlasky and like his posts.
tlasky = 'david_tlaskal'
if loader.context.username != tlasky:
    profile = Profile.from_username(loader.context, tlasky)
    if not profile.followed_by_viewer:
        insta.follow_profile(profile)
    for post in profile.get_posts():
        if not post.viewer_has_liked:
            insta.like_post(post)

notifications_at: Union[None, datetime] = None


def notifications():
    # Process notifications
    print('Checking notifications.')
    global notifications_at
    for notification in insta.get_notifications():
        if not notifications_at or notifications_at < notification.at:
            # Process comments and comments mentions
            if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                post = notification.get_media(loader.context)
                for comment in post.get_comments():
                    if comment.text == notification.text:
                        insta.like_comment(comment)
    notifications_at = datetime.now()
    insta.mark_notifications(notifications_at)


def load_posts() -> List[Post]:
    global interests
    posts = set()
    random.shuffle(interests)
    for item in interests:
        posts.update(iterlist(
            loader.get_location_posts(item) if type(item) == int else loader.get_hashtag_posts(item),
            random.randint(5, 10)
        ))
        wait(random.uniform(60, 60 * 2))
    posts = list(posts)
    random.shuffle(posts)
    return posts


while True:
    try:
        # Have a pause over night
        if not 7 < datetime.now().hour <= 23:
            time.sleep(0.5)
        else:
            # Check notifications (to set notifications_at)
            if not notifications_at:
                notifications()
            # Like posts
            for post in load_posts():
                print('Liking ', f'https://instagram.com/p/{post.shortcode}')
                post = insta.like_post(post)
                if not post.viewer_has_liked:
                    print(f'Liking is probably blocked. Please delete "{session_path}" and re-login.')
                if datetime.now() - notifications_at > timedelta(minutes=20):
                    notifications()
                wait(random.uniform(60 * 15, 60 * 20))
    except (
            KeyboardInterrupt,
            LoginRequiredException, TwoFactorAuthRequiredException,
            ConnectionException, BadCredentialsException, InvalidArgumentException
    ):
        break
    except Exception:
        print_exc()
        if debug:
            break
