"""
HH.ru OAuth2 support

Take a look to https://github.com/hhru/api/blob/master/docs/authorization.md

You need to register OAuth site here:
https://dev.hh.ru/

Then update your settings values using registration information

"""

import urllib2
import json

from social.backends.oauth import BaseOAuth2

class HhruOAuth2(BaseOAuth2):
    """HH.ru OAuth2 support"""
    name = 'hhru-oauth2'
    AUTHORIZATION_URL = 'https://hh.ru/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://m.hh.ru/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'id'

    def auth_complete(self, *args, **kwargs):
        try:
            return super(HhruOAuth2, self).auth_complete(*args, **kwargs)
        except urllib2.HTTPError:
            raise Exception(self)

    def get_user_details(self, response):
        username = ''.join(('hhru_', str(response.get('id'))))
        return {'username': username,
                'email': response.get('email'),
                'first_name': response.get('first_name'),
                'last_name': response.get('last_name'),
                'employer': response.get('employer'),
                'is_employer': response.get('is_employer')}

    def user_data(self, access_token, response, *args, **kwargs):
        """Loads user data from service"""
        request = urllib2.Request("http://api.hh.ru/me",
                                  headers={"Authorization": "Bearer {token}".format(token=access_token)})
        data = urllib2.urlopen(request).read()

        return json.loads(data)

