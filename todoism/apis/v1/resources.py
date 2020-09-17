#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from todoism.models import User, Item
from todoism.apis.v1 import api_v1
from flask.views import MethodView
from flask import jsonify, request, g, current_app, url_for
from todoism.apis.v1.schemas import user_schema, item_schema, items_schema
from todoism.apis.v1.auth import get_token, validate_token, auth_required, generate_token
from todoism.apis.v1.errors import api_abort, ValidationError
from todoism.extensions import db


class IndexAPI(MethodView):
    def get(self):
        return jsonify({
            'api_verion': 'v1.0',
            'api_basr_url': 'http://127.0.0.1:8080/api/v1',
        })


class AuthTokenAPI(MethodView):
    def post(self):
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')
        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant_type must be password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            return api_abort(code=400, message='Invild username or password')

        token, expiration = generate_token(user)
        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


def get_item_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        raise ValidationError('The item body was empty or invalid')
    return body


class ItemAPI(MethodView):
    decorators = [auth_required]

    # 获取item
    def get(self, item_id):
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        return jsonify(item_schema(item))

    # 更新item
    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.body = get_item_body()
        db.session.commit()
        return '', 204

    # item设置为done
    def patch(self, item_id):
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.done = True
        db.session.commit()
        return '', 204

    # 删除item
    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify(user_schema(g.current_user))


class ItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).paginate(page, per_page)
        items = pagination.items
        current = url_for('api_v1.items', page=page, _external=True)
        if pagination.has_prev:
            prev = url_for('api_v1', page=page - 1, _external=True)
        else:
            prev = None
        if pagination.has_next:
            next = url_for('api_v1.items', page=page + 1, _external=True)
        else:
            next = None
        return jsonify(items_schema(items, current, prev, next, pagination))

    def post(self):
        item = Item(body=get_item_body(), author=g.current_user)
        db.session.add(item)
        db.session.commit()
        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('api_v1.item', item_id=item.id, _external=True)
        return response


class ActiveItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).paginate(page, per_page)
        items = pagination.items
        current = url_for('api_v1.items', page=page, _external=True)
        if pagination.has_prev:
            prev = url_for('api_v1.active_items', page=page -1, _external=True)
        else:
            prev = None
        if pagination.has_next:
            next = url_for('api_v1.active_items', page=page + 1, _external=True)
        else:
            next = None
        return jsonify(items_schema(items, current, prev, next, pagination))


class CompletedItemAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=True).paginate(page, per_page)
        items = pagination.items
        current = url_for('api_v1.items', page=page, _external=True)
        if pagination.has_prev:
            prev = url_for('api_v1.completed_items', page=page-1, _external=True)
        else:
            prev = None
        if pagination.has_next:
            next = url_for('api_v1.completed_items', page=page+1, _external=True)
        else:
            next = None
        return jsonify(items_schema(items, current, prev, next, pagination))

    def delete(self):
        Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()
        return '', 204


api_v1.add_url_rule('/',  view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
api_v1.add_url_rule('/user/items/<int:item_id>', view_func=ItemAPI.as_view('item'), methods=['GET', 'PUT', 'PATCH', 'DELETE'])
api_v1.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])
api_v1.add_url_rule('/user/items', view_func=ItemsAPI.as_view('items'), methods=['GET', 'POST'])
api_v1.add_url_rule('/user/items/active', view_func=ActiveItemsAPI.as_view('active_items'), methods=['GET'])
api_v1.add_url_rule('/user/items/complete', view_func=CompletedItemAPI.as_view('completed_items'), methods=['GET', 'DELETE'])
