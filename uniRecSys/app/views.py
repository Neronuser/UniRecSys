from uniRecSys.app import app, api
from uniRecSys.app.models import ItemResource, UserResource, ScoreResource
from flask.ext.mongorest.views import ResourceView
from flask.ext.mongorest import operators as ops
from flask.ext.mongorest import methods


@api.register(name='items', url='/items/')
class ItemView(ResourceView):
    resource = ItemResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@api.register(name='users', url='/users/')
class UserView(ResourceView):
    resource = UserResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@api.register(name='scores', url='/scores/')
class ScoreView(ResourceView):
    resource = ScoreResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@app.route("/")
def hello():
    return "Hello World!"
