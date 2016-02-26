from flask import Flask, render_template, jsonify, abort, request, Response, redirect, session, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask.ext.classy import FlaskView
import requests
from datetime import datetime
import json
from flask_oauth import OAuth
from urllib2 import Request, urlopen, URLError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Memes"
REDIRECT_URI = "/oauth2callback"
db = SQLAlchemy(app)
admin = Admin(app, name='tops', template_mode='bootstrap3')
oauth = OAuth()
app.config.update(
    GOOGLE_CONSUMER_KEY='655313797231-1m1s6aqi70aedl9k6bh6h3trbpge8t6r.apps.googleusercontent.com',
    GOOGLE_CONSUMER_SECRET='i9N3ZAmve-5ljeDcBoSDXHyA',
    SECRET_KEY='just a secret key, to confound the bad guys',
    DEBUG=True
)
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config['GOOGLE_CONSUMER_KEY'],
                          consumer_secret=app.config['GOOGLE_CONSUMER_SECRET'])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    tops = db.Column(db.Integer)
    total_tops = db.Column(db.Integer)

class TopsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(256))
    approved = db.Column(db.Boolean, default=True)
    to_user_email = db.Column(db.String)
    from_user_email = db.Column(db.String)
    datetime = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<TopsEvent (from %r to %r)>' % (self.from_user_id, self.to_user_id)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class RedeemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref="redeem_events")
    redeemable_id = db.Column(db.Integer, db.ForeignKey('redeemable.id'))
    redeemable = db.relationship("Redeemable", backref="redeem_events")
    datetime = db.Column(db.DateTime, default=datetime.now())
    approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<RedeemableEvent user:%r redeemable_id:%r>' % (self.user_id, self.redeemable_id)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Redeemable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    image = db.Column(db.String(256))
    description = db.Column(db.String(256))
    value = db.Column(db.Integer)

    def __repr__(self):
        return '<Redeemable %r>' % (self.name)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}



@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0]
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    session['email'] = json.loads(res.read())['email']
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        user = User(
            email=session['email'],
            tops=0,
            total_tops=0
        )
        db.session.add(user)
        db.session.commit()
    return render_template('index.html')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/logout')
def logout():
    session.pop('access_token')
    return redirect(url_for('login'))

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')



def authenticate():
    url = "https://app.pingboard.com/oauth/token"
    querystring = {"grant_type":"client_credentials"}
    payload = "client_id=698fb86824586a1b700e882933c966968e60c2061f529b146f2977bd43372ec8&client_secret=20ed6a86a904a1e76d4129b77dd2b1439733910f7a53f6bd60f37d9ca46557ba"
    headers = {
        'content-type': "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    data = json.loads(response.text)
    return data['access_token']

access_token = authenticate()


admin.add_view(ModelView(TopsEvent, db.session))
admin.add_view(ModelView(RedeemEvent, db.session))
admin.add_view(ModelView(Redeemable, db.session))
admin.add_view(ModelView(User, db.session))

@app.route('/redeem')
def redeem():
    print session['email']
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return redirect(url_for('login'))
    redeemables = Redeemable.query.all()
    return render_template('redeem.html', redeemables=redeemables, points=user.tops)

@app.route('/resetdb')
def resetdb():
    db.create_all()
    return "Done"

@app.route('/points/')
def points(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        abort(404)
    return jsonify(tops=user.tops, total_tops=user.total_tops)

# API
class UsersView(FlaskView):
    def index(self):
        url = "https://app.pingboard.com/api/v2/search/users"
        querystring = {
            "q": request.args.get('q') or 'a'
        }
        headers = {
            'authorization': "Bearer " + access_token,
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        result = []
        for x in response.json()['hits']['hits']:
            # print x
            result.append({
                "score": x['_score'],
                "name": x['_source']['first_name'] + ' ' + x['_source']['last_name'],
                "avatar_url": x['_source']['avatar_url'],
                "id": int(x['_id'])
            })
        # result = []
        # for i in loaded_result[:10]:
        #     result[i] = json

        return jsonify(data=result)

    def get(self, id):
        url = "https://app.pingboard.com/api/v2/users/" + id
        querystring = {
            "include": "linked_accounts,groups"
        }

        headers = {
            'authorization': "Bearer " + access_token,
        }

        response = requests.request("GET", url, headers=headers, params=querystring)


        return Response(response=response.text,
                        status=200,
                        mimetype="application/json")


class RedeemEventsView(FlaskView):
    def index(self):
        events = [x.to_dict() for x in RedeemEvent.query.all()]
        return jsonify(data=events)

    def get(self, id):
        event = RedeemEvent.query.get(id)
        if not event:
            abort(404)
        return jsonify(event.to_dict())

    def post(self):
        # print [x.to_dict() for x in Redeemable.query.all()]
        # print request.json['redeemable_id']
        user = User.query.filter_by(email=session['email']).first()
        redeemable = Redeemable.query.get(request.json['redeemable_id'])
        if not redeemable:
            abort(404)
        event = RedeemEvent(
            user=user,
            redeemable=redeemable,
        )
        user.tops -= 1;
        db.session.add(user)
        db.session.add(event)
        db.session.commit()
        return jsonify(success=True)

    def put(self, id):
        pass

class TopsEventsView(FlaskView):
    def index(self):
        events = [x.to_dict() for x in TopsEvent.query.all()]
        return jsonify(data=events)

    def get(self, id):
        event = RedeemaEvent.query.get(id)
        if not event:
            abort(404)
        return jsonify(event.to_dict())

    def post(self):
        user = User.query.filter_by(email=request.json['to_user_email']).first()
        if not user:
            user = User(
                email=request.json['to_user_email'],
                tops=0,
                total_tops=0
            )
        user.tops += 1
        user.total_tops += 1
        event = TopsEvent(
            reason=request.json['reason'],
            to_user_email=request.json['to_user_email'],
            from_user_email=session['email'],
        )
        db.session.add(user)
        db.session.add(event)
        db.session.commit()
        return jsonify(success=True)

    def put(self, id):
        pass

RedeemEventsView.register(app)
TopsEventsView.register(app)
UsersView.register(app)

if __name__ == '__main__':
    app.run(debug=True)
