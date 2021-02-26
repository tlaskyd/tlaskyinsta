from instances import *
from pprint import pprint

response = insta.session.get(
    'https://i.instagram.com/api/v1/direct_v2/get_presence/'
)
pprint(response.request.headers)
pprint(response.headers)
pprint(response.text)
