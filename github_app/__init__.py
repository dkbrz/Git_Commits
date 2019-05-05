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
from collections import defaultdict
from sqlalchemy import func, select, and_, desc
from werkzeug.security import generate_password_hash, check_password_hash

from flask import after_this_request, session, jsonify, current_app, send_from_directory, make_response
from flask import Flask, Response
from flask import render_template, request, redirect, url_for

from github_app.models import *
from github_app.settings import APP_ROOT, CONFIG, LINK_PREFIX, W2V

import numpy as np
import scipy.stats as st
from gensim.models import KeyedVectors

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
w2v = KeyedVectors.load_word2vec_format(W2V)


RELATIONS = {1: 'acl', 2: 'acl:relcl', 3: 'advcl', 4: 'advmod', 5: 'amod', 6: 'appos', 7: 'aux', 8: 'aux:pass',
             9: 'case', 10: 'cc', 11: 'cc:preconj', 12: 'ccomp', 13: 'compound', 14: 'compound:prt', 15: 'conj',
             16: 'cop', 17: 'csubj', 18: 'csubj:pass', 19: 'dep', 20: 'det', 21: 'det:predet', 22: 'discourse',
             23: 'dislocated', 24: 'expl', 25: 'fixed', 26: 'flat', 27: 'flat:foreign', 28: 'goeswith', 29: 'iobj',
             30: 'list', 31: 'mark', 32: 'nmod', 33: 'nmod:npmod', 34: 'nmod:poss', 35: 'nmod:tmod', 36: 'nsubj',
             37: 'nsubj:pass', 38: 'nummod', 39: 'obj', 40: 'obl', 41: 'obl:npmod', 42: 'obl:tmod', 43: 'orphan',
             44: 'parataxis', 45: 'punct', 46: 'reparandum', 47: 'root', 48: 'vocative', 49: 'xcomp'}

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
    return render_template('entry.html', result=result)


@app.route("/clusters", methods=['POST', 'GET'])
def clusters():
    return render_template('clusters.html')


@app.route("/freqdict", methods=['POST', 'GET'])
def freqdict():
    return render_template('freqdict.html')


def search(word):
    result = {'freq':{}, 'grammars':[]}
    if word in w2v:
        result['neighbours'] = [(Lemmas.query.filter_by(lemma=w).one_or_none(), score) for w, score in w2v.most_similar(word, topn=20)]
    result['idx'] = Lemmas.query.filter_by(lemma=word).one_or_none()
    if result['idx']:
        # ----------------- frequency --------------------------------------------------
        freq = Frequency.query.filter_by(id_lemma=result['idx'].id).one_or_none()
        compare = {i.language_name: i.totalcount_unigrams for i in Languages.query.all()}
        result['freq']['languages'] = [
            ('C', freq.c, freq.c/compare['C']*1000000),
            ('C#', freq.csh, freq.csh/compare['C#'] * 1000000),
            ('C++', freq.cpp, freq.cpp/compare['C++']*1000000),
            ('CSS', freq.css, freq.css/compare['CSS']*1000000),
            ('Go', freq.go, freq.go/compare['Go']*1000000),
            ('HTML', freq.html, freq.html/compare['HTML']*1000000),
            ('Java', freq.java, freq.java/compare['Java']*1000000),
            ('JavaScript', freq.javascript, freq.javascript/compare['JavaScript']*1000000),
            ('Objective-C', freq.objc, freq.objc/compare['Objective-C']*1000000),
            ('PHP', freq.php, freq.php/compare['PHP']*1000000),
            ('Python', freq.python, freq.python/compare['Python']*1000000),
            ('Ruby', freq.ruby, freq.ruby/compare['Ruby']*1000000),
            ('Shell', freq.shell, freq.shell/compare['Shell']*1000000),
            ('Swift',freq.swift, freq.swift/compare['Swift']*1000000),
            ('TypeScript', freq.typescript, freq.typescript/compare['TypeScript']*1000000),
            ('Total', freq.total, ''),
        ]
        a = np.array([float(i[2]) for i in result['freq']['languages'] if i[2] != ''])
        result['freq']['languages_conf'] = st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))
        TOTAL = freq.total
        # TO-DO month, n-th in language

        # ------------------ POS ----------------------------------------------------------

        # group grammar variants

        #grammars = LGP.query.filter(LGP.id_lemma == result['idx'].id).join(Grammar,
        #                                                                   Grammar.id == LGP.id_grammar
        #                                                                   ).add_columns(Grammar.string_format,
        #                                                                                 Grammar.pos).all()

        grammar_idxs_full = LGP.query.filter(LGP.id_lemma == result['idx'].id).all()
        #print(grammar_idxs_full)
        grammar_idxs_id_grammar = [i.id_grammar for i in grammar_idxs_full]
        #print(grammar_idxs_id_grammar)
        grammar_idxs_id_lgp = {i.id: i.id_grammar for i in grammar_idxs_full}
        grammar_idxs_id_lgp_reverse = {i.id_grammar: i.id for i in grammar_idxs_full}
        grammar_idxs_full = {i.id: i for i in grammar_idxs_full}
        #print(grammar_idxs_id_lgp)
        grammars = {i.id: i for i in Grammar.query.filter(Grammar.id.in_(grammar_idxs_id_grammar)).all()}
        #print(grammars)
        pos = defaultdict(list)
        #print(pos)
        for key in grammars:
            pos[grammars[key].pos].append(key)
        #print(pos)
        result['grammars'] = {
            key:
                [
                    {'grammar': grammars[i],
                     'lgf': grammar_idxs_full[grammar_idxs_id_lgp_reverse[i]]
                     }
                    for i in sorted(pos[key],
                                    key=lambda x: grammar_idxs_full[grammar_idxs_id_lgp_reverse[x]].totalcount,
                                    reverse=True)
                ]
            for key in sorted(pos,
                              key=lambda x: sum(grammar_idxs_full[grammar_idxs_id_lgp_reverse[k]].totalcount for k in pos[x]),
                              reverse=True)
            if sum(grammar_idxs_full[grammar_idxs_id_lgp_reverse[key]].totalcount for key in pos[key]) > TOTAL/100
        }

        head_rel = RelationPairs.query.filter_by(id_head=result['idx'].id)
        relations = head_rel.with_entities(
                        RelationPairs.id_relation,
                        func.sum(RelationPairs.total_count)
                    ).group_by(
                        RelationPairs.id_relation
                    ).having(
                        func.sum(RelationPairs.total_count) > TOTAL/100
                    ).order_by(
                        desc(func.sum(RelationPairs.total_count))
                    ).all()
        #print('relations |||', relations)
        head_res = [
                        [
                            RELATIONS[i[0]],
                             i[1],
                             [
                                (Lemmas.query.filter_by(id=j[0]).one_or_none(),
                                 j[2], round(j[3], 1), round(j[4], 1), round(j[5], 1))
                                for j in head_rel.filter_by(
                                         id_relation=i[0]
                                    ).with_entities(
                                        RelationPairs.id_dependent,
                                        RelationPairs.id_relation,
                                        RelationPairs.total_count,
                                        RelationPairs.tscore,
                                        RelationPairs.mi,
                                        RelationPairs.logdice
                                    ).filter(
                                        RelationPairs.total_count > max(25, i[1]/100)
                                    ).order_by(
                                        desc(RelationPairs.logdice)
                                    ).limit(25).all()
                            ]
                        ]
                    for i in relations
                ]
        #print(head_res)
        result['head'] = head_res

        dep_rel = RelationPairs.query.filter_by(id_dependent=result['idx'].id)
        relations = dep_rel.with_entities(
            RelationPairs.id_relation,
            func.sum(RelationPairs.total_count)
        ).group_by(
            RelationPairs.id_relation
        ).having(
            func.sum(RelationPairs.total_count) > TOTAL / 100
        ).order_by(
            desc(func.sum(RelationPairs.total_count))
        ).all()
        # print('relations |||', relations)
        dep_res = [
            [
                RELATIONS[i[0]],
                i[1],
                [
                    (Lemmas.query.filter_by(id=j[0]).one_or_none(),
                     j[2], round(j[3], 1), round(j[4], 1), round(j[5], 1))
                    for j in dep_rel.filter_by(
                        id_relation=i[0]
                    ).with_entities(
                        RelationPairs.id_head,
                        RelationPairs.id_relation,
                        RelationPairs.total_count,
                        RelationPairs.tscore,
                        RelationPairs.mi,
                        RelationPairs.logdice
                    ).filter(
                        RelationPairs.total_count > max(25, i[1] / 100)
                    ).order_by(
                        desc(RelationPairs.logdice)
                    ).limit(25).all()
                ]
            ]
            for i in relations
        ]
        # print(head_res)
        result['dep'] = dep_res
    return result