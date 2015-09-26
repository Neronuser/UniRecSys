from uniRecSys.app import db, bcrypt
from flask.ext.mongorest.resources import Resource


class User(db.Document):
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(max_length=100)


class UserResource(Resource):
    document = User

    def create_object(self, data=None, save=True, parent_resources=None):
        kwargs = {}
        data = data or self.data
        data['password'] = bcrypt.generate_password_hash(data['password'])
        for field in super(UserResource, self).get_fields():
            if field in self.document._fields.keys() and field not in self.readonly_fields and (type(data) is list or (type(data) is dict and (field in data))):
                kwargs[field] = self._get('create_object', data, field, parent_resources=parent_resources)
        obj = self.document(**kwargs)
        if save:
            self._save(obj)
        return obj


class Item(db.Document):
    name = db.StringField(unique=True, max_length=20)
    description = db.StringField(max_length=200)


class ItemResource(Resource):
    document = Item


class Score(db.Document):
    score = db.IntField(min_value=1, max_value=5)
    user = db.ReferenceField(User)
    item = db.ReferenceField(Item)


class ScoreResource(Resource):
    document = Score
