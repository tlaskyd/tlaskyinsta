import random
from config import *
from tlasky_insta import *
from traceback import print_exc
from datetime import datetime, timedelta

loader = Instaloader()
safe_login(
    loader,
    username, password,
    session_path
)
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
            wait(random.uniform(60, 120))


def process_notifications():
    # Process notifications
    print('Checking notifications.')
    for notification in insta.get_notifications():
        if insta.last_notifications_at < notification.at:
            # Process comments and comments mentions
            if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                post = notification.get_media(loader.context)
                for comment in post.get_comments():
                    if comment.text == notification.text:
                        insta.like_comment(comment)
    insta.mark_notifications()


def load_posts() -> List[Post]:
    print('Loading posts.')
    global interests
    # Set because we don't want duplicated posts
    posts = set()
    random.shuffle(interests)
    for item in interests:
        posts.update(iterlist(
            loader.get_location_posts(item) if type(item) == int else loader.get_hashtag_posts(item),
            random.randint(5, 10)
        ))
        wait(random.uniform(60, 60 * 2))
    # List because we can shuffle it
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
            if not insta.last_notifications_at:
                process_notifications()
            # Like posts
            for post in random.choices(load_posts(), k=random.randint(5, 15)):
                print('Liking ', f'https://instagram.com/p/{post.shortcode}')
                if not insta.like_post(post).viewer_has_liked:
                    # Confirm that image was really liked
                    print(f'Liking is probably blocked. Please delete "{session_path}" and re-login.')
                # Process notifications at least every ~ 20+ minutes
                if datetime.now() - insta.last_notifications_at > timedelta(minutes=20):
                    process_notifications()
                # Wait to avoid rate limit or likes block
                wait(random.uniform(60 * 20, 60 * 30))
            wait(random.uniform(60 * 15, 60 * 30))
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
