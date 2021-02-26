from instances import *
from instaloader import Profile

profile = Profile.from_username(context, loader.context.username)

followees = list(profile.get_followees())
followers = list(profile.get_followers())

non_followers = sorted(
    [
        followee
        for followee in followees
        if followee not in followers
    ],
    key=lambda p: p.username
)

for non_follower in non_followers:
    print(non_follower.username)
