from uniRecSys.app import app, api, bcrypt
from uniRecSys.app.models import *
from flask import request, session, flash, redirect, url_for, render_template, jsonify
from flask.ext.mongorest.views import ResourceView
import numpy as np
from collections import defaultdict
from scipy.spatial import distance
from flask.ext.mongorest import operators as ops
from flask.ext.mongorest import methods


@api.register(name='items', url='/items/')
class ItemView(ResourceView):
    """
    Item view, REST API for Create, Update, Fetch and List
    """
    resource = ItemResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@api.register(name='users', url='/users/')
class UserView(ResourceView):
    """
    User view, REST API for Create, Update, Fetch and List
    """
    resource = UserResource
    methods = [methods.Create]


@api.register(name='scores', url='/scores/')
class ScoreView(ResourceView):
    """
    Score view, REST API for Create, Update, Fetch and List
    """
    resource = ScoreResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login method for tracking user behavior and authentification

    :return: Flask.Response
    """
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
                return jsonify({"status": [{"error": error}, {"result": "logged in"}]})
        except:
            error = "User does not exist"
            flash('User does not exist')
    return jsonify({"status": [{"error": error}, {"result": "error"}]})


@app.route('/logout')
def logout():
    """Ending user session

    :return: Flask.Response
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return jsonify({"status": "logged out"})


@app.route('/recommend')
def recommend():
    """User-based collaborative filtering recommendation engine algorithm

    :return: Flask.Response -- JSON Item objects
    """
    this_user = User.objects.get(email=session["this_user"]['email'])
    user_ids = User.objects().only('id').all()
    item_ids = Item.objects().only('id').all()
    scores = Score.objects().all()
    user_item_score = [((score.user.id, score.item.id), score.score) for score in scores]
    this_user_item_score = list(filter(lambda x: x[0][0] == this_user.id, user_item_score))
    this_item_score = list(map(lambda x: (x[0][1], x[1]), this_user_item_score))
    this_average_item_score = np.mean(list(map(lambda x: x[1], this_item_score)))
    similarities = []
    for user_id in user_ids:
        if user_id.id == this_user.id:
            continue
        that_user_item_score = list(filter(lambda x: x[0][0] == user_id.id, user_item_score))
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
        that_scores = np.array(that_scores)
        that_user_similarity = (user_id, 1 - distance.cosine(this_scores, that_scores))
        similarities.append(that_user_similarity)
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    top = similarities[:20]
    top_ids = list(map(lambda x: x[0].id, top))
    top_user_item_score = list(filter(lambda x: x[0][0] in top_ids, user_item_score))
    top_user_score = list(map(lambda x: (x[0][0], x[1]), top_user_item_score))
    # GroupBy analog
    d = defaultdict(list)
    for tag, num in top_user_score:
        d[tag].append(num)
    top_user_scores = list(d.items())
    top_user_average = [(x[0], np.mean(x[1])) for x in top_user_scores]
    top_similarities = [x[1] for x in top]
    k = 1 / np.sum(np.absolute(top_similarities))
    this_items = list(map(lambda x: x[0], this_item_score))
    unrated_items = list(filter(lambda x: x in this_items, [x.id for x in item_ids]))
    ratings = []
    for item in unrated_items:
        current_item_user_score = [(x[0][0], x[1]) for x in top_user_item_score if x[0][1] == item]
        current_scores = np.array([x[1] for x in current_item_user_score])
        current_top_users = [x[0] for x in current_item_user_score]
        new_top_user_average = list(filter(lambda x: x[0] in current_top_users, top_user_average))
        new_top_average = np.array([x[1] for x in new_top_user_average])
        top_ten_ratings_i = current_scores - new_top_average
        top_user_sim = list(filter(lambda x: x[0].id in current_top_users, top))
        top_sim = [x[1] for x in top_user_sim]
        rating = (item, this_average_item_score + k * np.dot(top_sim, top_ten_ratings_i))
        ratings.append(rating)
    ratings = sorted(ratings, key=lambda x: x[1], reverse=True)
    recommendation = ratings[:10]
    recommend_items = Item.objects(id__in=[rec[0] for rec in recommendation]).all()
    return recommend_items.to_json()


@app.route('/search/<string:name>')
def search(name):
    """Searching items by name

    :param name: String query string(key)
    :return: Flask.Response -- JSON Item objects
    """
    searched = Item.objects(name__icontains=name).all()
    return searched.to_json()

