# from folklore_app.transliteration import *
from datetime import datetime
import copy
import functools
import gzip
import json
import math
import os
import random
import re
import time
import uuid
import xlsxwriter

from functools import wraps, update_wrapper
from sqlalchemy import func, select, and_
from werkzeug.security import generate_password_hash, check_password_hash

from flask import after_this_request, session, jsonify, current_app, send_from_directory, make_response
from flask import Flask, Response
from flask import render_template, request, redirect, url_for

from github_app.models import *
from github_app.settings import APP_ROOT, CONFIG, LINK_PREFIX



DB = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(CONFIG['USER'], CONFIG['PASSWORD'],
                                             CONFIG['HOST'], CONFIG['PORT'], CONFIG['DATABASE'])


def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['APPLICATION_ROOT'] = APP_ROOT
    app.config['SQLALCHEMY_DATABASE_URI'] = DB
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.secret_key = 'yyjzqy9ffY'
    db.app = app
    db.init_app(app)
    return app


app = create_app()
# app.route = prefix_route(app.route, '/foklore/')
# db.create_all()
# app.app_context().push()


@app.context_processor
def add_prefix():
    return dict(prefix=LINK_PREFIX)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/entry", methods=['POST', 'GET'])
def entry():
    result = None
    if request.args:
        word = request.args.get('word')
        result = search(word)
    return render_template('entry.html', result = result)


def search(word):
    result = {}
    result['idx'] = Lemmas.query.filter_by(lemma=word).one_or_none()
    if result['idx']:
        result['freq'] = Frequency.query.filter_by(id_lemma=result['idx'].id).one_or_none()
        result['compare'] = {i.language_name: i.totalcount_unigrams for i in Languages.query.all()}
        result['grammars'] = LGP.query.filter(LGP.id_lemma==result['idx'].id).join(Grammar, Grammar.id == LGP.id_grammar).add_columns(Grammar.string_format, Grammar.pos).all()
        #print(dir(result['grammars']), len(result['grammars']))
        print(result['grammars'])
    return result
