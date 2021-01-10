from typing import *
from enum import Enum
from datetime import datetime
from instaloader import InstaloaderContext, Post, Profile

from .utils import multikeys


class NotificationType(Enum):
    LIKE = 1
    COMMENT = 2
    NEW_FOLLOW = 3
    COMMENT_MENTION = 5


class Notification:
    def __init__(self, notification_type: NotificationType, at: datetime, userid: int, shortcode: Union[None, str],
                 text: Union[None, str]):
        self.type = notification_type
        self.at = at
        self.userid = userid
        self.shortcode = shortcode
        self.text = text

    def __repr__(self):
        return self.__class__.__name__ + '(' + ', '.join(f'{key}={value}' for key, value in self.__dict__.items()) + ')'

    @classmethod
    def from_dict(cls, dct) -> 'Notification':
        return Notification(
            notification_type=NotificationType(multikeys(dct, 'node', 'type')),
            at=datetime.fromtimestamp(multikeys(dct, 'node', 'timestamp')),
            userid=multikeys(dct, 'node', 'user', 'id'),
            shortcode=multikeys(dct, 'node', 'media', 'shortcode'),
            text=multikeys(dct, 'node', 'text', default=str())
        )

    def get_media(self, context: InstaloaderContext) -> Union[None, Post]:
        return Post.from_shortcode(context, self.shortcode) if self.shortcode else None

    def get_user(self, context: InstaloaderContext) -> Profile:
        return Profile.from_id(context, self.userid)
