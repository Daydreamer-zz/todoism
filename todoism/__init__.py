#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, click
from flask import Flask, render_template, jsonify
from flask_login import current_user
from todoism.settings import config
from todoism.extensions import db, csrf, login_manager
from todoism.models import User, Item
from todoism.blueprints.auth import auth_bp
from todoism.blueprints.home import home_bp
from todoism.blueprints.todo import todo_bp
from todoism.apis.v1 import api_v1


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('todoism')
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_template_context(app)
    return app


def register_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)  # api_v1蓝图不需要csrf_protect，从csrf中去除
    login_manager.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(api_v1, url_prefix='/api/v1')


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        if drop:
            click.confirm('This operation will delete all data, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables')
        db.create_all()
        click.echo('Initialized database.')


def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        response = jsonify(code=404, message='The request url was not found on the server')
        response.status_code = 404
        return response


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            active_items = 'Test'
        else:
            active_items = None
        return dict(active_items=active_items)