#!/usr/bin/env python
import os
import time
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


# initialization
from helper import helper
from helper.helper import Rank

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()



class Off(db.Model):
    __tablename__ = 'Off'
    id_off = db.Column(db.Integer, primary_key=True)
    offname = db.Column(db.String(32), index=True)
    km = db.Column(db.Integer)
    meetingPoint = db.relationship('gpxPoint', backref='off', lazy=True)
    endPoint = db.relationship('gpxPoint', backref='off', lazy=True)
    loop = db.Column(db.Boolean)
    owner = db.relationship('User', backref='off', lazy=True)
    gpx_url = db.Column(db.String(255))
    dplus = db.Column(db.Integer)
    after = db.Column(db.Boolean)
    estimateTime = db.Column(db.Float)
    detail = db.Column(db.String(255))

class Participant(db.Model):
    __tablename__ = 'Participant'
    id_participant = db.Column(db.Integer, primary_key=True)
    off = db.relationship('Off', backref='participant', lazy=True)
    runner = db.relationship('User', backref='participant', lazy=True)
    ridesharingFrom = db.relationship('gpxPoint', backref='participant', lazy=True)
    mark = db.Column(db.Integer)
    review = db.Column(db.String(255))



class offPhoto(db.Model):
    __tablename__ = 'offPhoto'
    id_photo = db.Column(db.Integer, primary_key=True)
    owner = db.relationship('User', backref='offPhoto', lazy=True)
    off = db.relationship('Off', backref='offPhoto', lazy=True)
    photo_url = db.Column(db.String(255))

class gpxPoint(db.Model):
    __tablename__ = 'gpxPoint'
    id_gpx = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(255))
    longitude = db.Column(db.String(255))
    detail = db.Column(db.String(255))
    owner = db.relationship('User', backref='off', lazy=True)

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id_gpx': self.id_gpx,
            'latitude':self.latitude,
            'longitude':self.longitude,
            'detail':self.detail,
            'owner':self.owner.serialize()
        }


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    mail = db.Column(db.String(128))
    kikourou_url = db.Column(db.String(128))
    rank =  db.Column(db.Integer)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'username':self.username,
            'mail':self.mail,
            'kikourou_url':self.kikourou_url,
            'rank':self.rank
        }

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True





#--------------------------ADMIN-------------------------------
@app.route('/api/admin/users')
@auth.login_required
def get_users():
    users = User.query.order_by(User.username).all()
    data=[]
    for u in users:
        data.append(u.serialize())
    print(data)
    if not users :
        return jsonify({})
    if g.user.rank != helper.ADMIN:
        abort(403)
    return jsonify(data)


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

#--------------------------gpxPoint-------------------------------

@app.route("/api/gps/owner/<int:id>",  methods=['GET'])
@auth.login_required
def get_gpx_point_by_owner(id):
    user= User.query.filter_by(id=id).first()
    if user is None:
        abort(400)    # not existing user

    points = gpxPoint.query.filter_by(owner=user).all()
    data = []
    for u in points:
        data.append(u.serialize())

    if not points :
        return jsonify({})
    if g.user.rank != helper.USER :
        abort(403)
    return jsonify(data)

@app.route("/api/gps/<int:id>",  methods=['GET'])
@auth.login_required
def get_gpx_point(id):
    point = gpxPoint.query.get(id)
    if not point :
        return jsonify({})
    if g.user.rank != helper.USER :
        abort(403)
    return jsonify({'id':point.id_gpx,'latitude': point.latitude, 'longitude':point.longitude, 'detail':point.detail})

@app.route('/api/gps/registration', methods=['POST'])
def new_gpx():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    detail = request.json.get('detail')
    owner = request.json.get('id_user')


    if User.query.filter_by(owner=owner).first() is None:
        abort(400)  # not existing user
    if latitude is None and longitude is None or detail is None:
        abort(400)
    gpx = gpxPoint()
    gpx.owner = User.query.filter_by(id=owner).first()
    gpx.latitude = latitude
    gpx.longitude=longitude
    gpx.detail=detail
    db.session.add(gpx)
    db.session.commit()
    return (jsonify({'gpx': gpx.id_gpx}), 201,
            {'Location': url_for('get_gpx', id=gpx.id_gpx, _external=True)})



    #--------------------------OFF-------------------------------
@app.route('/api/offs/registration', methods=['POST'])
def new_off():
    offname = request.json.get('offname')
    km = request.json.get('km')
    meetingPoint = request.json.get('id_meetingpoint')
    endPoint = request.json.get('id_endpoint')
    loop = request.json.get('loop')
    owner = request.json.get('id_user')
    gpx_url = request.json.get('gpx_url')
    dplus = request.json.get('dplus')
    after = request.json.get('after')
    estimateTime = request.json.get('estimateTime')
    detail = request.json.get('detail')
    if offname is None or km is None or meetingPoint is None or endPoint is None or loop is None or owner is None:
        abort(400)  # missing arguments
    if User.query.filter_by(id=owner).first() is None:
        abort(400)    # not existing user
    off = Off(offname=offname)
    off.km = km
    off.meetingPoint = gpxPoint.query.filter_by(id_gpx=meetingPoint).first()
    off.endPoint = gpxPoint.query.filter_by(id_gpx=endPoint).first()
    off.loop=bool(loop)
    off.owner = User.query.filter_by(id=owner).first()
    off.gpx_url = gpx_url
    off.dplus = int(dplus)
    off.after=bool(after)
    off.estimateTime=float(estimateTime)
    off.detail=detail
    db.session.add(off)
    db.session.commit()
    return (jsonify({'username': off.offname}), 201,
            {'Location': url_for('get_off', id=off.id_off, _external=True)})


#--------------------------USER-------------------------------

@app.route('/api/user/registration', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    mail = request.json.get('mail')
    kikourou_url = request.json.get('kikourou_url')
    rank = Rank.USER.value
    if username is None or password is None or mail is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    user.mail = mail
    user.kikourou_url = kikourou_url
    user.rank = rank
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/user/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if not user :
        return jsonify({})
    if g.user.rank != helper.ADMIN and g.user.id != id:
        abort(403)
    return jsonify({'id':user.id,'username': user.username, 'mail':user.mail, 'kikourou':user.kikourou_url})



@app.route('/')
def get_api_endpoint():
    return jsonify(helper.api_endpoint())

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
