from path_file import *


from testMethods import getCookie, getUserIdAndEntity, getResponseCode, parseApiRoutes, \
    replaceUserId, replaceProductId, getResponseCode

#from marketplace.api_folder.utils.user_utils import get_user_by_email

from marketplace.api_folder.utils.consumer_utils import get_consumer_by_id, get_all_consumers, \
    post_consumer, put_consumer, delete_consumer_by_id, upload_consumer_image



import requests
import unittest
from mock import Mock



class TestCase(unittest.TestCase):
    unittest.TestLoader.sortTestMethodsUsing = None
    def setUp(self):

        self.user = Mock()
        self.producer = Mock()
        
        #login data
        self.user.email = 'berenice.cavalcanti@example.com'
        self.producer.email = 'annabelle.denys@example.com'
        self.pw = '123123'

        self.product_id = 3

        #edit profile
        self.user.first_name = 'Abra'
        self.user.last_name = 'Cadabra'
        self.user.patronymic = 'Redisovic'
        self.user.phone_number = '81212121'

        self.base_url = 'http://127.0.0.1:8000'
        self.login_url = self.base_url + '/api/v1/login'


    def testLogin(self):

        cookie, response = getCookie(self.login_url, self.user.email, self.pw)

        self.assertEqual(201, response.status_code)
        self.assertIn('remember_token', cookie)
        self.assertIn('session', cookie)

        print('Test Login is OK.\n')

    def testLogout(self):
        logout_url = self.base_url + '/api/v1/logout'
        response = requests.Session().get(logout_url)

        self.assertEqual(201, response.status_code)
        self.assertNotIn('session', response.cookies)

        print('Test Logout is OK.\n')

    def testResponseAuthPages(self):

        #(remember_token and session in cookie) and response status_code
        cookie, response = getCookie(self.login_url, self.user.email, self.pw)
        user_id, user_entity = getUserIdAndEntity(response)

        routes = parseApiRoutes()
        for route in routes['auth']:

            if user_entity == 'producer' and '<producer_id>' in route:
                test_url = replaceUserId(self.base_url + route, user_id)
                test_url = replaceProductId(test_url, self.product_id)
                req = requests.session().get(test_url, cookies=cookie)
                self.assertEqual(200, req.status_code)

            elif user_entity == 'consumer' and '<user_id>' in route:
                test_url = replaceUserId(self.base_url + route, user_id)
                req = requests.session().get(test_url, cookies=cookie)
                self.assertEqual(200, req.status_code)
        print('Test Auth user pages is OK.\n')

        """TODO: add test /email_confirm/<token>"""


    def testUserAdd(self):
        consumer = post_consumer(args)

    def testUserDelete(self):
        msg = delete_consumer_by_id(id)

    def testUserEdit(self):
        cookie, response = getCookie(self.login_url, self.user.email, self.pw)
        user_id, user_entity = getUserIdAndEntity(response)
        url = self.base_url + '/user/edit/' + str(user_id)

        print(url)

        consumer = get_consumer_by_id(user_id)
        print(consumer.email)

        args = {'email': 'a@ma.ru'}

        consumer = put_consumer(args, user_id)
        print(consumer.email)

        args = {'email': 'berenice.cavalcanti@example.com'}
        consumer = put_consumer(args, user_id)
        print(consumer.email)

if __name__ == '__main__':
    unittest.main()