from typing import *
from instaloader import *
from datetime import datetime
from json import JSONDecodeError
from requests import Session, Response

from .utils import multikeys
from .notification import Notification

PostCommentType = Union[PostComment, PostCommentAnswer]


class TlaskyInsta:
    def __init__(self, loader: Instaloader, quiet=False):
        assert loader.test_login(), 'Please provide logged-in Instaloader.'
        self.loader = loader
        self.last_notifications_at: Union[None, datetime] = None
        self.quiet = quiet

    @property
    def session(self) -> Session:
        # Because loader.context._session is private attribute.
        return getattr(self.loader.context, '_session')

    def log(self, *args, **kwargs):
        if not self.quiet:
            print(*args, **kwargs)

    def _check_response(self, response: Response) -> Response:
        # self.log(' *', response.request.url, response.request.body) # Just for debugging
        self.log(' *', response.request.method, response.url, response.status_code, end=' ')
        try:
            self.log(response.json()['status'])
        except KeyError:
            self.log()
        except JSONDecodeError:
            self.log('\n' + response.text)
        return response

    def like_post(self, post: Post) -> Post:
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/likes/{post.mediaid}/like/'
        ))
        return Post.from_mediaid(self.loader.context, post.mediaid)

    def unlike_post(self, post: Post) -> Post:
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/likes/{post.mediaid}/unlike/'
        ))
        return Post.from_mediaid(self.loader.context, post.mediaid)

    def comment_post(self, post: Post, text: str, reply_to: PostCommentType = None) -> PostCommentType:
        response = self._check_response(self.session.post(
            f'https://www.instagram.com/web/comments/{post.mediaid}/add/',
            data=dict(
                comment_text=text,
                replied_to_comment_id=reply_to.id if reply_to else None
            )
        ))
        return PostCommentAnswer(
            id=multikeys(response.json(), 'id'),
            created_at_utc=datetime.fromtimestamp(multikeys(response.json(), 'created_time')),
            text=multikeys(response.json(), 'text'),
            owner=Profile.from_id(self.loader.context, multikeys(response.json(), 'from', 'id')),
            likes_count=0
        )

    def uncomment_post(self, post: Post, comment: PostCommentType):
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/comments/{post.mediaid}/delete/{comment.id}/'
        ))

    def like_comment(self, comment: PostCommentType):
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/comments/like/{comment.id}/'
        ))

    def unlike_comment(self, comment: PostCommentType):
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/comments/unlike/{comment.id}/'
        ))

    def follow_profile(self, profile: Profile):
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/friendships/{profile.userid}/follow/'
        ))

    def unfollow_profile(self, profile: Profile):
        self._check_response(self.session.post(
            f'https://www.instagram.com/web/friendships/{profile.userid}/unfollow/',
        ))

    def seen_story(self, story: Story, item: StoryItem, seen_at: datetime = None):
        # TODO: Fix
        self._check_response(self.session.post(
            f'https://www.instagram.com/stories/reel/seen',
            data=dict(
                reelMediaId=item.mediaid,
                reelMediaOwnerId=item.owner_id,
                reelId=story.owner_id,
                reelMediaTakenAt=int(item.date.timestamp()),
                viewSeenAt=int((seen_at or datetime.now()).timestamp()),
            )
        ))

    def get_notifications(self, reels: bool = False) -> List[Notification]:
        response = self._check_response(self.session.get(
            'https://www.instagram.com/accounts/activity/',
            params={
                '__a': 1,
                'include_reel': str(reels).lower()
            }
        ))
        notifications = sorted(
            [
                Notification.from_dict(notification_dict)
                for notification_dict in multikeys(
                response.json(),
                'graphql', 'user', 'activity_feed', 'edge_web_activity_feed', 'edges'
            )
            ],
            key=lambda n: n.at,
            reverse=True
        )
        self.last_notifications_at = notifications[0].at
        return notifications

    def mark_notifications(self, from_date: datetime = None):
        self._check_response(self.session.post(
            'https://www.instagram.com/web/activity/mark_checked/',
            data=dict(
                timestamp=(from_date or self.last_notifications_at or datetime.now()).timestamp()
            )
        ))
