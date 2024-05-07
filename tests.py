import unittest
from http import HTTPStatus
from blogwise import create_app

class BlogwiseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('blogwise.settings')
        self.client = self.app.test_client()

    def test_homepage_success_200_OK(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

if __name__ == '__main__':
    unittest.main()

