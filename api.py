#!/usr/bin/env python
import os
import time
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


# initialization
from helper import rank
from helper.rank import Rank

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
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


@app.route('/api/registration', methods=['POST'])
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



@app.route('/api/users')
@auth.login_required
def get_users():
    users = User.query.order_by(User.username).all()
    data=[]
    for u in users:
        data.append(u.serialize())
    print(data)
    if not users :
        return jsonify({})
    if g.user.rank != rank.ADMIN:
        abort(403)
    return jsonify(data)



@app.route('/api/user/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if not user :
        return jsonify({})
    if g.user.rank != rank.ADMIN and g.user.id != id:
        abort(403)
    return jsonify({'id':user.id,'username': user.username, 'mail':user.mail, 'kikourou':user.kikourou_url})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
