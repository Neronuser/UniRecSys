from uniRecSys.app import app as app2
import json
import unittest
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface


class UniRecSysTestCase(unittest.TestCase):
    def setUp(self):
        app2.config['MONGODB_DB'] = "testing"
        app2.config['TESTING'] = True
        db = MongoEngine(app2)
        self.app = app2
        self.app.session_interface = MongoEngineSessionInterface(db)
        self.db = db
        self.c = self.app.test_client()

    def tearDown(self):
        self.db.connection.drop_database("testing")

    def test_users(self):
        resp = self.c.post('/users/', data=json.dumps({
            "email": "12341@dot.net",
            "login": "1234",
            "password": "toor"
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data)["login"], "1234")

        resp = self.c.get('/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(json.loads(resp.data)['data']) > 0)

    def test_hello_world(self):
        resp = self.c.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.decode('utf-8'), "Hello World!")


if __name__ == '__main__':
    unittest.main()
