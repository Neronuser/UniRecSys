from uniRecSys.app import bcrypt, app as app2
from uniRecSys.app.models import User, Item, Score
import json
import unittest
import numpy as np
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface


class UniRecSysTestCase(unittest.TestCase):
    """
    A set of unittests
    """
    def setUp(self):
        """
        Sets up a testing database and connects to it
        """
        app2.config['MONGODB_DB'] = "testing"
        app2.config['TESTING'] = True
        db = MongoEngine(app2)
        self.app = app2
        self.app.session_interface = MongoEngineSessionInterface(db)
        self.db = db
        self.c = self.app.test_client()

    def tearDown(self):
        """
        Drops the database after testing is finished
        """
        self.db.connection.drop_database("testing")

    def test_recommendations(self):
        """
        Test routine for user creation, login and getting recommendations
        """
        for i in range(100):
            User(email=str(i) + "@dot.net", password=bcrypt.generate_password_hash("toor")).save()
            Item(name=str(i), description="bla").save()
        users = User.objects().all()
        self.items = Item.objects().all()
        for i in range(1000):
            try:
                Score(score=np.random.randint(1, 6), user=users[np.random.randint(0, 100)].id,
                      item=self.items[np.random.randint(0, 100)].id).save()
            except:
                continue

        user1 = self.c.post('/users/', data=json.dumps({
            "email": "12341@dot.net",
            "password": "toor"
        }))
        self.assertEqual(user1.status_code, 200)
        self.assertEqual(json.loads(user1.data)["email"], "12341@dot.net")

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
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(json.loads(resp.data)) > 0)

    def test_search(self):
        """
        Test routine for search item by name
        """
        Item(name="Valid string", description="bla").save()
        Item(name="String of hope", description="bla").save()
        Item(name="No str here", description="bla").save()
        resp = self.c.get('/search/string')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(json.loads(resp.data)) == 2)

    def test_create_score(self):
        """
        Test routine for score creation
        """
        item = Item(name="Valid string", description="bla").save()
        user = User(email="bb@bb.com", password="kooo").save()
        score = self.c.post('/scores/', data=json.dumps({
            "score": 2,
            "user": str(user.id),
            "item": str(item.id)
        }))
        self.assertTrue(json.loads(score.data)["score"] == 2)

    def test_update_score(self):
        """
        Test routine for updating the score value by a given user for a given item
        """
        item = Item(name="Valid string", description="bla").save()
        user = User(email="bb@bb.com", password="kooo").save()
        Score(score=3, user=user.id, item=item.id).save()
        current_score = Score.objects(score=3).first()
        new_rating = current_score.score + 1
        new_score = self.c.put('/scores/' + str(current_score.id) + '/', data=json.dumps({
            "score": new_rating,
            "user": str(current_score.user.id),
            "item": str(current_score.item.id)
        }))
        self.assertTrue(json.loads(new_score.data)["score"] == 4)

    def test_create_item(self):
        """
        Test routine for item creation
        """
        item1 = self.c.post('/items/', data=json.dumps({
            "name": "Barrett M82",
            "description": "50. caliber semi-automatic sniper rifle"
        }))
        self.assertEqual(item1.status_code, 200)
        self.assertEqual(json.loads(item1.data)["name"], "Barrett M82")

    def test_update_item(self):
        """
        Test routine for updating the item value(name and description)
        """
        item = Item(name="Barrett M82", description="50. caliber semi-automatic sniper rifle").save()
        new = ("Barett M107", "Barett M82 improved")
        new_item = self.c.put('/items/' + str(item.id) + '/', data=json.dumps({
            "name": new[0],
            "description": new[1]
        }))
        self.assertTrue(json.loads(new_item.data)["name"] == new[0])
        self.assertTrue(json.loads(new_item.data)["description"] == new[1])


if __name__ == '__main__':
    unittest.main()
