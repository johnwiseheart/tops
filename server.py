from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
admin = Admin(app, name='tops', template_mode='bootstrap3')


class TopsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(256))
    approved = db.Column(db.Boolean)
    to_user_id = db.Column(db.Integer)
    from_user_id = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)

    def __repr__(self):
        return '<TopsEvent (from %r to %r)>' % (self.from_user_id, self.to_user_id)


class RedeemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    redeemable_id = db.Column(db.Integer, db.ForeignKey('redeemable.id'))
    redeemable = db.relationship("Redeemable", backref="redeem_events")
    datetime = db.Column(db.DateTime)
    approved = db.Column(db.Boolean)

    def __repr__(self):
        return '<RedeemableEvent user:%r redeemable_id:%r>' % (self.user_id, self.redeemable_id)


class Redeemable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    image = db.Column(db.String(256))
    description = db.Column(db.String(256))
    value = db.Column(db.Integer)

    def __repr__(self):
        return '<Redeemable %r>' % (self.name)

admin.add_view(ModelView(TopsEvent, db.session))
admin.add_view(ModelView(RedeemEvent, db.session))
admin.add_view(ModelView(Redeemable, db.session))
db.create_all()

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
