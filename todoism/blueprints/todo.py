#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, jsonify

todo_bp = Blueprint('todo', __name__)


@todo_bp.route('/app')
def app():
    return jsonify(message='this is a app page')
