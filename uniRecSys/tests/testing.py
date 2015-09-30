from uniRecSys.app import bcrypt, app as app2
from uniRecSys.app.models import User, Item, Score
import json
import unittest
import numpy as np
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
        for i in range(100):
            User(email=str(i) + "@dot.net", password=bcrypt.generate_password_hash("toor")).save()
            Item(name=str(i), description="bla").save()
        users = User.objects().all()
        self.items = Item.objects().all()
        for i in range(500):
            try:
                Score(score=np.random.randint(1, 6), user=users[np.random.randint(0, 100)].id,
                      item=self.items[np.random.randint(0, 100)].id).save()
            except:
                continue

    def tearDown(self):
        self.db.connection.drop_database("testing")

    def test_users(self):
        user1 = self.c.post('/users/', data=json.dumps({
            "email": "12341@dot.net",
            "password": "toor"
        }))
        self.assertEqual(user1.status_code, 200)
        self.assertEqual(json.loads(user1.data)["email"], "12341@dot.net")

        resp = self.c.get('/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(json.loads(resp.data)['data']) > 0)

        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        login = self.c.post('/login', data={
            "email": "12341@dot.net",
            "password": "toor"
        }, headers=headers)

        for i in range(30):
            try:
                Score(score=np.random.randint(1, 6), user=json.loads(user1.data)['id'],
                    item=self.items[np.random.randint(0, 50)].id).save()
            except:
                continue
        resp = self.c.get('/recommend')

    def test_search(self):
        Item(name="Valid string", description="bla").save()
        Item(name="String of hope", description="bla").save()
        Item(name="No str here", description="bla").save()
        resp = self.c.get('/search/string')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(json.loads(resp.data)) == 2)


if __name__ == '__main__':
    unittest.main()
