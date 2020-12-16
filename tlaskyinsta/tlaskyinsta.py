import json
from urllib.parse import urljoin
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
        self.base_url = 'https://instagram.com/'

    def __repr__(self):
        return f'{self.__class__.__name__}(loader={self.loader})'

    """
    ETC
    """

    @property
    def loader_session(self) -> Session:
        # Accessing private attribute of InstaloaderContext
        return getattr(self.loader.context, '_session')

    @staticmethod
    def _status_check(response: Response):
        # Raise exception if bad response
        try:
            assert response.json().get('status') == 'ok'
        except (json.JSONDecodeError, AssertionError):
            raise InvalidResponse(f'Invalid response.\n{response.text}')

    def url_for(self, *args: Any) -> str:
        return urljoin(
            self.base_url,
            '/'.join(str(arg) for arg in args)
        )

    """
    Posts
    """

    def like_post(self, post: Post):
        """
        Like post.
        :param post:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'likes', post.mediaid, 'like'
        ))
        self._status_check(response)

    def unlike_post(self, post: Post):
        """
        Unlike post.
        :param post:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'likes', post.mediaid, 'unlike'
        ))
        self._status_check(response)

    """
    Comments
    """

    def comment(self, post: Post, text: str, reply_to: Union[PostComment, PostCommentAnswer, None] = None):
        """
        Add comment.
        :param post:
        :param text:
        :param reply_to:
        :return:
        """
        response = self.loader_session.post(
            self.url_for(
                'web', 'comments', post.mediaid, 'add'
            ),
            data=dict(
                comment_text=text,
                replied_to_comment_id=reply_to.id if reply_to else None
            )
        )
        self._status_check(response)

    def delete_comment(self, post: Post, comment: Union[PostComment, PostCommentAnswer]):
        """
        Remove comment.
        :param post:
        :param comment:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'comments', post.mediaid, 'delete', comment.id
        ))
        self._status_check(response)

    def like_comment(self, comment: Union[PostComment, PostCommentAnswer]):
        # TODO: Fix... For some reason does not work
        """
        Like comment or comment response.
        :param comment:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'comments', 'like', comment.id
        ))
        self._status_check(response)

    def unlike_comment(self, comment: Union[PostComment, PostCommentAnswer]):
        # TODO: Fix... Same as like_comment(...)
        """
        Unlike comment or comment response.
        :param comment:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'comments', 'unlike', comment.id
        ))
        self._status_check(response)

    """
    Follow / Unfollow
    """

    def follow(self, profile: Profile):
        """
        Follow user.
        :param profile:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'friendships', profile.userid, 'follow'
        ))
        self._status_check(response)

    def unfollow(self, profile: Profile):
        """
        Unfollow user.
        :param profile:
        :return:
        """
        response = self.loader_session.post(self.url_for(
            'web', 'friendships', profile.userid, 'unfollow'
        ))
        self._status_check(response)

    """
    Activity / Notifications
    """

    def _activity(self) -> Dict[str, Any]:
        # Activity json shortcut.
        response = self.loader_session.get(
            self.url_for('accounts', 'activity'),
            params=json_params()
        )
        return multi_keys(
            response.json(),
            'graphql', 'user',
        )

    def notifications(self) -> List[Notification]:
        """
        Get notifications.
        :return:
        """
        return [
            Notification.from_dict(self.loader.context, notification_dct)
            for notification_dct in multi_keys(
                self._activity(),
                'activity_feed', 'edge_web_activity_feed', 'edges'
            )
        ]

    def follow_requests(self) -> Dict[str, Any]:
        # TODO: Please send me your follow request json. My ig profile is public, so I don't know it's structure.
        """
        Follow requests.
        :return:
        """
        return multi_keys(
            self._activity(),
            'edge_follow_requests', 'edges'
        )
