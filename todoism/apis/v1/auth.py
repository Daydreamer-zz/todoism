#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import g, current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from todoism.apis.v1.errors import api_abort, invalid_token, token_missing
from todoism.models import User
from functools import wraps


def generate_token(user):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id}).decode('ascii')
    return token, expiration


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def get_token():
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token_type, token = get_token()
        if request.method != 'OPTIONS':
            if token_type is None or token_type != 'Bearer':
                return api_abort(400, 'The token type must be Bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()
        return func(*args, **kwargs)
    return inner