#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from todoism.apis.v1 import api_v1


# api接口不能使用abort(xxx）返回错误，单独编写一个错误处理函数
def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')  # 错误消息没指定就从werkzeug的HTTP_STATUS_CODES错误码字典中取出
    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response


def invalid_token():
    response = api_abort(401, message='invalid_token', error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(code=401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


class ValidationError(ValueError):
    pass

@api_v1.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.args[0])