#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from todoism.models import Item, User
from todoism.extensions import db
todo_bp = Blueprint('todo', __name__)


# todoism首页(添加/展示 项目)
@todo_bp.route('/app')
@login_required
def app():
    all_count = Item.query.with_parent(current_user).count()
    active_count = Item.query.with_parent(current_user).filter_by(done=False).count()
    completed_count = Item.query.with_parent(current_user).filter_by(done=True).count()
    return render_template('_app.html', items=current_user.items, all_count=all_count, active_count=active_count, completed_count=completed_count)


# 添加事项
@todo_bp.route('/items/new', methods=['POST'])
@login_required
def new_item():
    data = request.get_json()
    if data is None or data['body'].strip() == '':
        return jsonify(message='Invalid item body'), 400
    item = Item(body=data['body'], author=current_user._get_current_object())
    db.session.add(item)
    db.session.commit()
    return jsonify(html=render_template('_item.html', item=item), message='+1')


# 修改item
@todo_bp.route('/item/<int:item_id>/edit', methods=["POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message='Permission denied'), 403
    data = request.get_json()
    if data is None or data['body'].strip() == '':
        return jsonify(message='Invalid item body'), 400
    item.body = data['body']
    db.session.commit()
    return jsonify(message='Item updated')

