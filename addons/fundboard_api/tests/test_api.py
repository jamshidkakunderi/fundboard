import requests

from odoo.tests import HttpCase
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import json

ROOT = "http://localhost:8070"
SUPERUSER_ID = 1
class TestAPI(HttpCase):

    def setUp(self):
        super().setUp()
        user =  self.env['res.users']
        self.user = user.sudo().with_context(no_reset_password=True)._create_user_from_template({
            'name': 'Test User',
            'login': 'test1@example.com',
            'password': 'test',
            'email': 'test1@example.com',

        })

        self.token = self.env['api.token'].create_token(self.user.id)
        self.partner = self.env['res.partner'].create({'name': 'Test partner'})
        self.client = Client(ROOT, BaseResponse)

    def test_01_login(self):
        # response = self.client.post('/api/login', json={'login': 'test', 'password': 'test'})
        suburl = "/api/login"
        url = ROOT + suburl
        payload = {'login': 'test1@example.com', 'password': 'test'}
        headers = {
            'Content-Type': 'application/json'
        }
        print("=======>>>>>>>before response")
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload))
        print("====>>>>try", response)
        res = json.loads(response.text)
        print(res)
        print(res.get("status"), '1')
        print("=========>>>>>>>>>>>Pass", suburl)
        print("========>>>>>", url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(res.get('status'), 'Login success')
        self.assertEqual(res.get('uid'), self.user.id)
        print('Login success')

    def test_02_logout(self):
        response = self.client.post('/api/logout', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('status'), 'logged out')

    def test_03_get_records(self):
        response = self.client.get('/api/res.partner', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(rec.get('id') == self.partner.id for rec in response.json))
