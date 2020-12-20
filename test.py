from credentials import *
from instaloader import *
from tlaskyinsta import *

insta = TlaskyInsta()
loader = insta.loader
context = loader.context

loader.load_session_from_file(username, session_filepath.replace('.json', '.pickle'))

print(insta.session.cookies)
print(insta.session.headers)

exit()

post = Post.from_shortcode(context, 'CI-VVHLI-2k')
if not post.viewer_has_liked:
    print('Like')
    insta.like_post(post)
else:
    print('Unlike')
    insta.unlike_post(post)
