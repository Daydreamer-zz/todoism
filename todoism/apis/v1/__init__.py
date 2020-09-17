#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__)

CORS(api_v1)


# 导入位置必须在此
from todoism.apis.v1 import resources