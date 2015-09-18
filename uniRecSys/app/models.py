from uniRecSys.app import db


class User(db.Document):
    email = db.EmailField(unique=True, required=True)
    login = db.StringFiels(unique=True, max_length=20)
    password = db.StringField(max_length=30)


class Item(db.Document):
    name = db.StringField(unique=True, max_length=20)
    description = db.StringField(max_length=200)


class Score(db.Document):
    score = db.IntField(min_value=1, max_value=5)
    user = db.ReferenceField(User)
    item = db.ReferenceField(Item)

