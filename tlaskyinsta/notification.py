from enum import Enum
from datetime import datetime
from instaloader import (
    InstaloaderContext,
    Post, Profile, PostComment, PostCommentAnswer
)

from .utils import *


class NotificationType(Enum):
    # TODO: Add all notification types.
    # I think there should be type for: tagging in posts, etc...
    LIKE = 1
    COMMENT = 2
    STARTED_FOLLOWING = 3


class Notification:
    def __init__(self, loader_context: InstaloaderContext,
                 uid: str, notification_type: NotificationType, at: datetime,
                 author_uid: int, media_sc: str, text: str = str()):
        self.context = loader_context
        self.id = uid
        self.type = notification_type
        self.at = at
        self.author_uid = author_uid
        self.media_sc = media_sc

        self._author: Union[None, Profile] = None
        self._media: Union[None, Post, Profile, PostComment, PostCommentAnswer] = None
        self._text = text

    def __repr__(self):
        return f'{self.__class__.__name__}(' + \
               ', '.join(f'{name}={getattr(self, name)}' for name in ['id', 'at', 'media']) + \
               ')'

    @property
    def author(self) -> Profile:
        if not self._author:
            self._author = Profile.from_id(self.context, self.author_uid)
        return self._author

    @property
    def media(self) -> Union[None, Post, Profile, PostComment, PostCommentAnswer]:
        if not self._media:
            if self.type is NotificationType.LIKE:
                self._media = Post.from_shortcode(self.context, self.media_sc)
            elif self.type is NotificationType.COMMENT:
                for comment in Post.from_shortcode(self.context, self.media_sc).get_comments():
                    if comment.text == self._text:
                        return comment
            elif self.type is NotificationType.STARTED_FOLLOWING:
                self._media = self.author
        return self._media

    @classmethod
    def from_dict(cls, loader_context: InstaloaderContext, dct: Dict[str, Any]) -> 'Notification':
        return Notification(
            loader_context=loader_context,
            uid=multi_keys(dct, 'node', 'id'),
            notification_type=NotificationType(multi_keys(dct, 'node', 'type')),
            at=datetime.fromtimestamp(multi_keys(dct, 'node', 'timestamp')),
            author_uid=multi_keys(dct, 'node', 'user', 'id'),
            media_sc=multi_keys(dct, 'node', 'media', 'shortcode'),
            text=multi_keys(dct, 'node', 'text')
        )
