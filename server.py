from flask import Flask, render_template, jsonify, abort, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask.ext.classy import FlaskView
import requests
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Memes"
db = SQLAlchemy(app)
admin = Admin(app, name='tops', template_mode='bootstrap3')

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

class TopsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(256))
    approved = db.Column(db.Boolean, default=True)
    to_user_name = db.Column(db.String)
    from_user_name = db.Column(db.String)
    datetime = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<TopsEvent (from %r to %r)>' % (self.from_user_id, self.to_user_id)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class RedeemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    redeemable_id = db.Column(db.Integer, db.ForeignKey('redeemable.id'))
    redeemable = db.relationship("Redeemable", backref="redeem_events")
    datetime = db.Column(db.DateTime, default=datetime.now())
    approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<RedeemableEvent user:%r redeemable_id:%r>' % (self.user_name, self.redeemable_id)

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

admin.add_view(ModelView(TopsEvent, db.session))
admin.add_view(ModelView(RedeemEvent, db.session))
admin.add_view(ModelView(Redeemable, db.session))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resetdb')
def resetdb():
    db.create_all()
    return "Done"


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
            print x
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


class RedeemablesView(FlaskView):
    def index(self):
        redeemables = [x.to_dict() for x in Redeemable.query.all()]
        return jsonify(data=redeemables)

    def get(self, id):
        redeemable = Redeemable.query.get(id)
        if not redeemable:
            abort(404)
        return jsonify(redeemable.to_dict())

class RedeemEventsView(FlaskView):
    def index(self):
        events = [x.to_dict() for x in RedeemableEvent.query.all()]
        return jsonify(data=events)

    def get(self, id):
        event = RedeemableEvent.query.get(id)
        if not event:
            abort(404)
        return jsonify(event.to_dict())

    def post(self):
        print [x.to_dict() for x in Redeemable.query.all()]
        print request.json['redeemable_id']

        redeemable = Redeemable.query.get(request.json['redeemable_id'])
        if not redeemable:
            abort(404)
        event = RedeemEvent(
            user_name=request.json['user_name'],
            redeemable=redeemable,
        )
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
        event = RedeemableEvent.query.get(id)
        if not event:
            abort(404)
        return jsonify(event.to_dict())

    def post(self):
        print request.json
        event = TopsEvent(
            reason=request.json['reason'],
            to_user_name=request.json['to_user_name'],
            from_user_name=request.json['from_user_name'],
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(success=True)

    def put(self, id):
        pass

RedeemablesView.register(app)
RedeemEventsView.register(app)
TopsEventsView.register(app)
UsersView.register(app)

if __name__ == '__main__':
    app.run(debug=True)
