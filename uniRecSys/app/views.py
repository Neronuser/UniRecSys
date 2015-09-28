from uniRecSys.app import app, api, bcrypt
from uniRecSys.app.models import *
from flask import request, session, flash, redirect, url_for, render_template
from flask.ext.mongorest.views import ResourceView
import numpy as np
from scipy.spatial import distance
import itertools
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


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/recommend')
def recommend():
    this_user = User.objects.get(email=session["this_user"]['email'])
    user_ids = User.objects().only('id').all()
    item_ids = Item.objects().only('id').all()
    scores = Score.objects().all()
    user_item = [x for x in itertools.product(user_ids, item_ids)]
    user_item_score = [(tup, score.score) for tup in user_item for score in scores]
    this_user_item_score = filter(lambda x: x[0][0] == this_user.id, user_item_score)
    this_item_score = list(map(lambda x: (x[0][1], x[1]), this_user_item_score))
    this_average_item_score = np.mean(list(map(lambda x: x[1], this_item_score)))
    similarities = []
    for user_id in user_ids:
        if user_id == this_user.id:
            continue
        that_user_item_score = filter(lambda x: x[0][0] == user_id, user_item_score)
        that_item_score = list(map(lambda x: (x[0][1], x[1]), that_user_item_score))
        this_scores = []
        that_scores = []
        for this in this_item_score:
            for that in that_item_score:
                if this[0] == that[0]:
                    this_scores.append(this[1])
                    that_scores.append(that[1])
        if len(this_scores) < 5:
            continue
        this_scores = np.array(this_scores)
        that_scores = np.array(this_scores)
        that_user_similarity = (user_id, 1 - distance.cosine(this_scores, that_scores))
        similarities.append(that_user_similarity)
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    top = similarities[:20]
    top_ids = list(map(lambda x: x[0], similarities))
    top_user_item_score = filter(lambda x: x[0][0] in top_ids, user_item_score)
    top_user_score = list(map(lambda x: (x[0][0], x[1]), top_user_item_score))
    top_user_scores = itertools.groupby(top_user_score, lambda x: x[0])
    top_user_average = [(x[0], np.mean(x[1])) for x in top_user_scores]
    top_average = [x[1] for x in top_user_average]
    top_similarities = [x[1] for x in top]
    k = 1 / np.sum(np.absolute(top_similarities))
    this_items = list(map(lambda x: x[0], this_item_score))
    unrated_items = filter(lambda x: x in this_items, item_ids)
    ratings = []
    for item in unrated_items:
        top_ten_ratings_i = np.array([x[1] for x in top_user_item_score if x[0][1] == item]) - top_average
        rating = (item, this_average_item_score + k * np.dot(top_similarities, top_ten_ratings_i))
        ratings.append(rating)
    ratings = sorted(ratings, key=lambda x: x[1], reverse=True)
    recommendation = ratings[:10]
    return recommendation



