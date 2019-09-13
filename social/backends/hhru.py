"""
HH.ru OAuth2 support

Take a look to https://github.com/hhru/api/blob/master/docs/authorization.md

You need to register OAuth site here:
https://dev.hh.ru/

Then update your settings values using registration information

"""

import urllib2
import json
import logging

from social.backends.oauth import BaseOAuth2

logger = logging.getLogger('social.auth')


class HhruOAuth2(BaseOAuth2):
    """HH.ru OAuth2 support"""
    name = 'hhru-oauth2'
    AUTHORIZATION_URL = 'https://hh.ru/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://hh.ru/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'id'

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
        try:
            data = fetch_request("http://api.hh.ru/me",
                                 headers={"Authorization": "Bearer {token}".format(token=access_token),
                                          "User-Agent": self.get_user_agent()})
        except urllib2.HTTPError as ex:
            logger.error("HTTPError. Token: {0}. Reason: {1}".format(access_token, ex))
            raise

        json_data = json.loads(data)
        if 'errors' in json_data:
            if all([json_data['errors'][0].get('type') == 'manager_accounts',
                    json_data['errors'][0].get('value') == 'used_manager_account_forbidden']):
                try:
                    data = fetch_request("http://api.hh.ru/manager_accounts/mine",
                                         headers={"Authorization": "Bearer {token}".format(token=access_token),
                                                  "User-Agent": self.get_user_agent()})
                except urllib2.HTTPError as ex:
                    logger.error("HTTPError. Token: {0}. Reason: {1}".format(access_token, ex))
                    raise
                managers = json.loads(data)
                if managers.get('primary_account_id') and not managers.get('is_primary_account_blocked'):
                    manager_id = managers.get('primary_account_id')
                else:
                    manager_id = managers['items'][0]['id']
                try:
                    data = fetch_request("http://api.hh.ru/me",
                                         headers={"Authorization": "Bearer {token}".format(token=access_token),
                                                  "User-Agent": self.get_user_agent(),
                                                  "X-Manager-Account-Id": manager_id})
                except urllib2.HTTPError as ex:
                    logger.error("HTTPError. Token: {0}. Reason: {1}".format(access_token, ex))
                    raise
                json_data = json.loads(data)

        return json_data


def fetch_request(url, headers={}):
    request = urllib2.Request(url, headers=headers)
    data = urllib2.urlopen(request).read()
    return data
