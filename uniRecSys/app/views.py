from uniRecSys.app import app, api, bcrypt
from uniRecSys.app.models import *
from flask import request, session, flash, redirect, url_for, render_template
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
    methods = [methods.Create, methods.Fetch, methods.List]


@api.register(name='scores', url='/scores/')
class ScoreView(ResourceView):
    resource = ScoreResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            this_user = User.objects.get(email=request.form['email'])
            if not bcrypt.check_password_hash(this_user.password, request.form['password']):
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                session['this_user'] = {'email': this_user.email}
                flash('You were logged in')
                # TODO: right redirect and test
                return redirect(url_for('index'))
        except:
            error = "User does not exist"
            flash('User does not exist')
    return render_template('login.html', error=error)
