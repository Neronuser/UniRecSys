from uniRecSys.app import db


class User(db.Document):
    email = db.StringField(required=True)
    login = db.StringFiels(max_length=20)
    password = db.StringField(max_length=30)


class Item(db.Document):
    name = db.StringField(max_length=20)
    description = db.StringField(max_length=200)


# TODO: class Score

