import os
import random
from config import *
from tlasky_insta import *
from datetime import datetime
from traceback import print_exc

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

while True:
    try:
        # Have a pause over night
        if 7 < datetime.now().hour <= 23:
            # Process notifications
            notifications_at: Union[None, datetime] = None
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

            # Load posts
            posts = set()
            random.shuffle(tags)
            for tag in tags:
                tag_posts = iterlist(
                    loader.get_hashtag_posts(tag),
                    10
                )
                posts.update(tag_posts)
                wait(random.uniform(60, 60 * 2))
            random.shuffle(locations)
            for loc in locations:
                loc_posts = iterlist(
                    loader.get_location_posts(loc),
                    10
                )
                posts.update(loc_posts)
                wait(random.uniform(60, 60 * 2))
            posts = list(posts)
            random.shuffle(posts)

            # Like posts
            for post in posts:
                print('Liking ', f'https://instagram.com/p/{post.shortcode}')
                post = insta.like_post(post)
                if not post.viewer_has_liked:
                    print(f'Liking is probably blocked. Please delete "{session_path}" and re-login.')
                wait(random.uniform(60 * 15, 60 * 20))
        else:
            time.sleep(0.5)
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
