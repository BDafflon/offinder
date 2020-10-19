#!/usr/bin/env python
import os
import time
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
from sqlalchemy import engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
# initialization
from helper import *

from helper.helper import Rank, api_endpoint, distance_between_coord

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    mail = db.Column(db.String(128))
    kikourou_url = db.Column(db.String(128))
    rank = db.Column(db.Integer)
    genre = db.Column(db.Integer)

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
            'username': self.username,
            'mail': self.mail,
            'kikourou_url': self.kikourou_url,
            'rank': self.rank
        }

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


class gpxPoint(db.Model):
    __tablename__ = 'gpxPoint'
    id_gpx = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(255))
    longitude = db.Column(db.String(255))
    detail = db.Column(db.String(255))
    owner = db.Column(db.Integer, db.ForeignKey('User.id'))

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id_gpx': self.id_gpx,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'detail': self.detail,
            'owner': self.owner
        }


class Off(db.Model):
    __tablename__ = 'Off'
    id_off = db.Column(db.Integer, primary_key=True)
    offname = db.Column(db.String(32), index=True)
    km = db.Column(db.Integer)
    meetingPoint = db.Column(db.Integer, db.ForeignKey('gpxPoint.id_gpx'))
    endPoint = db.Column(db.Integer, db.ForeignKey('gpxPoint.id_gpx'))
    loop = db.Column(db.Boolean)
    owner = db.Column(db.Integer, db.ForeignKey('User.id'))
    gpx_url = db.Column(db.String(255))
    dplus = db.Column(db.Integer)
    after = db.Column(db.Boolean)
    estimateTime = db.Column(db.Float)
    detail = db.Column(db.String(255))
    date_off = db.Column(db.Integer, nullable=False)
    limitParticipants = db.Column(db.Integer)
    public = db.Column(db.Boolean)
    iconOff_url=db.Column(db.String(255))

    def serialize(self):
        """Return object data in easily serializable format"""
        meeting = gpxPoint.query.filter_by(id_gpx=self.meetingPoint).first()
        endP = gpxPoint.query.filter_by(id_gpx=self.endPoint).first()
        return {
            'id_off':self.id_off,
            'offname': self.offname,
            'km': self.km,
             'id_endpoint': endP.serialize(),
             'id_meetingpoint': meeting.serialize(),
            'loop':self.loop,
             'id_user':self.owner,
             'gpx_url':self.gpx_url,
             'dplus':self.dplus,
             'after':self.after,
             'estimateTime':self.estimateTime,
             'detail':self.detail,
             'public':self.public,
             'limitParticipants':self.limitParticipants,
             'date_off':self.date_off,
            'iconOff_url':self.iconOff_url
            }


class team(db.Model):
    id_team = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(255))
    owner = db.Column(db.Integer, db.ForeignKey('User.id'))


class teamMate(db.Model):
    id_teammate = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('User.id'))
    id_team = db.Column(db.Integer, db.ForeignKey('team.id_team'))
    registration = db.Column(db.DateTime, nullable=False)


class offPhoto(db.Model):
    __tablename__ = 'offPhoto'
    id_photo = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('User.id'))
    off = db.Column(db.Integer, db.ForeignKey('Off.id_off'))
    photo_url = db.Column(db.String(255))
    public = db.Column(db.Boolean)


class Participant(db.Model):
    __tablename__ = 'Participant'
    id_participant = db.Column(db.Integer, primary_key=True)
    off = db.Column(db.Integer, db.ForeignKey('Off.id_off'))
    runner = db.Column(db.Integer, db.ForeignKey('User.id'))
    ridesharingFrom = db.Column(db.Integer, db.ForeignKey('gpxPoint.id_gpx'))
    mark = db.Column(db.Integer)
    review = db.Column(db.String(255))


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


# --------------------------ADMIN-------------------------------

#Check
@app.route('/api/admin/users')
@auth.login_required
def get_users():
    users = User.query.order_by(User.username).all()
    data = []
    for u in users:
        data.append(u.serialize())
    if not users:
        return jsonify({})
    print(g.user.serialize())
    if g.user.rank != Rank.ADMIN.value:
        abort(403)
    return jsonify(data)


#Check
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


# --------------------------gpxPoint-------------------------------
#Ckeck
@app.route("/api/gps/owner/<int:id>", methods=['GET'])
@auth.login_required
def get_gpx_point_by_owner(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(400)  # not existing user

    points = gpxPoint.query.filter_by(owner=id).all()
    data = []
    for u in points:
        data.append(u.serialize())

    if not points:
        return jsonify({})
    print(g.user.rank)
    if (g.user.rank != Rank.USER.value and g.user.id != id) and g.user.rank != Rank.ADMIN.value:
        abort(403)
    return jsonify(data)


#Check
@app.route("/api/gps/<int:id>", methods=['GET'])
@auth.login_required
def get_gpx_point(id):
    point = gpxPoint.query.get(id)
    if not point:
        return jsonify({})

    return jsonify(
        {'id': point.id_gpx, 'latitude': point.latitude, 'longitude': point.longitude, 'detail': point.detail})

#Check
@app.route('/api/gps/registration', methods=['POST'])
@auth.login_required
def new_gpx():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    detail = request.json.get('detail')
    print(request.json.get('id_owner'))
    owner = User.query.filter_by(id=request.json.get('id_owner')).first()

    if owner is None:
        abort(400)  # not existing user
    if latitude is None and longitude is None or detail is None:
        abort(400)
    gpx = gpxPoint()
    gpx.owner = owner.id
    gpx.latitude = latitude
    gpx.longitude = longitude
    gpx.detail = detail
    db.session.add(gpx)
    db.session.commit()
    return (jsonify({'gpx': gpx.id_gpx}), 201,
            {'Location': url_for('get_gpx_point', id=gpx.id_gpx, _external=True)})

# --------------------------OFF-------------------------------


#Check
@app.route('/api/offs/registration', methods=['POST'])
@auth.login_required
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
    public = request.json.get('public')
    limit = request.json.get('limitParticipants')
    dateoff = request.json.get('dateoff')
    iconOff_url = ""
    if offname is None or km is None or meetingPoint is None or endPoint is None or loop is None or owner is None:
        print("1")
        abort(400)  # missing arguments
    if User.query.filter_by(id=owner).first() is None:
        print("2")
        abort(400)  # not existing user
    if gpxPoint.query.filter_by(id_gpx=meetingPoint).first() is None :
        print("3")
        abort(400)  # not existing user
    if loop == 0 and gpxPoint.query.filter_by(id_gpx=endPoint).first() is None :
        print("4")
        abort(400)  # not existing user

    off = Off(offname=offname)
    off.km = km
    off.meetingPoint = meetingPoint
    off.endPoint = endPoint
    off.loop = bool(loop)
    off.owner = owner
    off.gpx_url = gpx_url
    off.dplus = int(dplus)
    off.after = bool(after)
    off.estimateTime = float(estimateTime)
    off.detail = detail
    off.public=bool(public)
    off.limitParticipants = limit
    off.date_off = dateoff
    off.iconOff_url = iconOff_url
    db.session.add(off)
    db.session.commit()
    return (jsonify({'username': off.offname}), 201,
            {'Location': url_for('get_off', id=off.id_off, _external=True)})

#Check
@app.route('/api/off/<int:id>')
@auth.login_required
def get_off(id):
    off = Off.query.get(id)
    if not off:
        return jsonify({})
    return jsonify(off.serialize())

#Check
@app.route('/api/off/date/<int:date_off>')
@auth.login_required
def get_off_date(date_off):
    off = Off.query.filter(Off.date_off>=date_off)
    if not off:
        return jsonify({})
    data=[]
    for o in off:
        data.append(o.serialize())

    return jsonify(data)

#Check
@app.route('/api/off/location/<string:lat>/<string:lon>/<int:dist>')
@auth.login_required
def get_off_location(lat,lon,dist):
    off = Off.query.order_by(Off.id_off).all()
    if not off:
        return jsonify({})
    data = []
    for o in off:
        meetingP=get_gpx_point(o.meetingPoint).json
        if meetingP is None:
            abort(400)

        distance = distance_between_coord(float(lat),float(lon),float(meetingP['latitude']),float(meetingP['longitude']))
        if distance<dist:
            data.append(o.serialize())

    return jsonify(data)

#Check
@app.route('/api/off/owner/<int:user>')
@auth.login_required
def get_off_by_owner(user):
    off = Off.query.filter_by(owner=user)
    if not off:
        return jsonify({})
    data=[]
    for o in off:
        data.append(o.serialize())

    return jsonify(data)

@app.route("/api/off/participant/<int:id>")
@auth.login_required
def get_off_by_participant(id):
    Session = sessionmaker(bind=engine)
    session = Session()

    for p,o in session.query(Participant, Off).filter(Participant.off == Off.id_off).all():
        print(o)


    return jsonify({})


# --------------------------PARTICIPANT-------------------------------
@app.route('/api/participant/registration', methods=['POST'])
@auth.login_required
def new_participant():
    off = request.json.get('off')
    runner = request.json.get('runner')

    runner_ext = User.query.filter_by(id=runner).first()
    off_ext = Off.query.filter_by(id_off=off).first()

    if runner_ext is None or off_ext is None:
        abort(400)  # not existing user
    if runner != g.user.id:
        abort(403)

    participant = Participant()
    participant.off = off
    participant.runner = runner

    db.session.add(participant)
    db.session.commit()
    return (jsonify({'gpx': participant.id_participant}), 201,
            {})

# --------------------------USER-------------------------------

@app.route('/api/user/registration', methods=['POST'])
def new_user():
    print( request.args)
    username = request.json.get('username')
    password = request.json.get('password')
    mail = request.json.get('mail')
    kikourou_url = request.json.get('kikourou_url')
    rank = Rank.USER.value
    if username is None or password is None or mail is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        print("existing")
        abort(400)  # existing user
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
    if not user:
        return jsonify({})
    if g.user.rank != Rank.ADMIN.value and g.user.id != id:
        abort(403)
    return jsonify(user.serialize())


@app.route('/')
def get_api_endpoint():
    return jsonify(api_endpoint())


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()

    app.run(debug=True)
