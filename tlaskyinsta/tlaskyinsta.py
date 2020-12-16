import json
from requests import Session, Response
from instaloader import (
    Instaloader,
    Post, PostComment, PostCommentAnswer,
    Profile
)

from .utils import *
from .exceptions import *
from .notification import Notification


class TlaskyInsta:
    def __init__(self, loader: Instaloader = None):
        self.loader = loader or Instaloader(sleep=False, quiet=True)

    def __repr__(self):
        return f'{self.__class__.__name__}(loader={self.loader})'

    """
    ETC
    """

    @property
    def loader_session(self) -> Session:
        return getattr(self.loader.context, '_session')

    @staticmethod
    def _status_check(response: Response):
        try:
            assert response.json().get('status') == 'ok'
        except (json.JSONDecodeError, AssertionError):
            raise InvalidResponse(f'Invalid response.\n{response.text}')

    """
    Posts
    """

    def like_post(self, post: Post):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/likes/{post.mediaid}/like/'
        )
        self._status_check(response)

    def unlike_post(self, post: Post):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/likes/{post.mediaid}/unlike/'
        )
        self._status_check(response)

    """
    Comments
    """

    def comment(self, post: Post, text: str, reply_to: Union[PostComment, PostCommentAnswer, None] = None):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/comments/{post.mediaid}/add/',
            data=dict(
                comment_text=text,
                replied_to_comment_id=reply_to.id if reply_to else None
            )
        )
        self._status_check(response)

    def delete_comment(self, post: Post, comment: Union[PostComment, PostCommentAnswer]):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/comments/{post.mediaid}/delete/{comment.id}/'
        )
        self._status_check(response)

    def like_comment(self, comment: Union[PostComment, PostCommentAnswer]):
        # TODO: Fix... For some reason does not work
        response = self.loader_session.post(
            f'https://www.instagram.com/web/comments/like/{comment.id}/'
        )
        self._status_check(response)

    def unlike_comment(self, comment: Union[PostComment, PostCommentAnswer]):
        # TODO: Fix... Same as like_comment(...)
        response = self.loader_session.post(
            f'https://www.instagram.com/web/comments/unlike/{comment.id}/'
        )
        self._status_check(response)

    """
    Follow / Unfollow
    """

    def follow(self, profile: Profile):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/friendships/{profile.userid}/follow/'
        )
        self._status_check(response)

    def unfollow(self, profile: Profile):
        response = self.loader_session.post(
            f'https://www.instagram.com/web/friendships/{profile.userid}/unfollow/'
        )
        self._status_check(response)

    """
    Activity / Notifications
    """

    def _activity(self) -> Dict[str, Any]:
        response = self.loader_session.get(
            'https://www.instagram.com/accounts/activity/',
            params=json_params()
        )
        return multi_keys(
            response.json(),
            'graphql', 'user',
        )

    def notifications(self) -> List[Notification]:
        return [
            Notification.from_dict(self.loader.context, notification_dct)
            for notification_dct in multi_keys(
                self._activity(),
                'activity_feed', 'edge_web_activity_feed', 'edges'
            )
        ]

    def follow_requests(self) -> Dict[str, Any]:
        return multi_keys(
            self._activity(),
            'edge_follow_requests', 'edges'
        )
