#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, url_for, jsonify, render_template
from flask_login import current_user, login_user, logout_user, login_required
from todoism.models import User, Item
from todoism.extensions import db
from faker import Faker

auth_bp = Blueprint('auth', __name__)
fake = Faker()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('todo.app'))
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user is not None and user.validate_password(password):
            login_user(user)
            return jsonify(message='Login success')
        return jsonify(message='Invalid useranme or password'), 400
    return render_template('_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
     logout_user()
     return jsonify(message='Logout success')


@auth_bp.route('/register')
def register():
    db.drop_all()
    db.create_all()
    username = 'shz'
    password = '199747'
    user = User(username=username)
    user.set_password_hash(password=password)
    db.session.add(user)
    db.session.commit()

    item = Item(body='Witness something truly majestic', author=user)
    item2 = Item(body='Help a complete stranger', author=user)
    item3 = Item(body='Drive a motorcycle on the Great Wall of China', author=user)
    item4 = Item(body='Sit on the Great Egyptian Pyramids', done=True, author=user)
    db.session.add_all([item, item2, item3, item4])
    db.session.commit()

    return jsonify(username=username, password=password, message='Generate success')