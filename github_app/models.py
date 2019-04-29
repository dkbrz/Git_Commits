from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Examples(db.Model):

    __tablename__ = 'examples'
    
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    text = db.Column('text', db.Text)
    id_user = db.Column('id_user', db.Integer, db.ForeignKey('repos.id'))
    id_repo = db.Column('id_repo', db.Integer, db.ForeignKey('repos.gh_id'))


class Frequency(db.Model):

    __tablename__ = 'frequency_dict'

    id_lemma = db.Column('id_lemma', db.Integer, db.ForeignKey('lemmas.id'),
                primary_key=True, autoincrement=True, back_populates="lemmas")
    c = db.Column('c', db.Integer)
    csh = db.Column('csh', db.Integer)
    cpp = db.Column('cpp', db.Integer)
    css = db.Column('css', db.Integer)
    go = db.Column('go', db.Integer)
    html = db.Column('html', db.Integer)
    java = db.Column('java', db.Integer)
    javascript = db.Column('javascript', db.Integer)
    objc = db.Column('objc', db.Integer)
    php = db.Column('php', db.Integer)
    python = db.Column('python', db.Integer)
    ruby = db.Column('ruby', db.Integer)
    shell = db.Column('shell', db.Integer)
    swift = db.Column('swift', db.Integer)
    typescript = db.Column('typescript', db.Integer)
    other = db.Column('other', db.Integer)
    total = db.Column('total', db.Integer)


class Grammar(db.Model):
    __tablename__ = 'grammar'

    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True, back_populates="lemma_grammar_pairs")
    string_format = db.Column('string_format', db.Text)
    pos = db.Column('pos', db.Text)

    Abbr = db.Column('Abbr', db.Text)
    Case = db.Column('Case', db.Text)
    Definite = db.Column('Definite', db.Text)
    Degree = db.Column('Degree', db.Text)
    Foreign = db.Column('Foreign', db.Text)
    Gender = db.Column('Gender', db.Text)
    Mood = db.Column('Mood', db.Text)
    Number = db.Column('Number', db.Text)
    NumType = db.Column('NumType', db.Text)
    Person = db.Column('Person', db.Text)
    Poss = db.Column('Poss', db.Text)
    PronType = db.Column('PronType', db.Text)
    Reflex = db.Column('Reflex', db.Text)
    Tense = db.Column('Tense', db.Text)
    Typo = db.Column('Typo', db.Text)
    VerbForm = db.Column('VerbForm', db.Text)
    Voice = db.Column('Voice', db.Text)


class Languages(db.Model):
    __tablename__ = 'languages'

    id = db.Column('id', db.Integer,
                         primary_key=True, autoincrement=True,)
    language_name = db.Column('language_name', db.Text)
    totalcount_unigrams = db.Column('totalcount_unigrams', db.Integer)


class LGP(db.Model):
    __tablename__ = 'lemma_grammar_pairs'

    id = db.Column('id', db.Integer,
                         primary_key=True, autoincrement=True)
    id_lemma = db.Column('id_lemma', db.Integer)
    id_grammar = db.Column('id_grammar', db.Integer, db.ForeignKey('grammar.id'))
    form = db.Column('form', db.Text)
    totalcount = db.Column('totalcount', db.Integer)
    #grammar = db.relationship('LGP', backref='grammar', uselist=False)


class Lemmas(db.Model):
    __tablename__ = 'lemmas'

    id = db.Column('id', db.Integer,
                         primary_key=True, autoincrement=True, back_populates="frequency_dict")
    lemma = db.Column('lemma', db.Text)


class RelationPairs(db.Model):
    __tablename__ = 'relation_pair'

    id = db.Column('id', db.Integer,primary_key=True, autoincrement=True)
    id_head = db.Column('id_head', db.Integer, back_populates="lemma_grammar_pairs")
    id_dependent = db.Column('id_dependent', db.Integer, back_populates="lemma_grammar_pairs")
    id_relation = db.Column('id_relation', db.Integer, back_populates="relations")
    id_example = db.Column('id_example', db.Integer, back_populates="examples")
    idx_diff = db.Column('idx_diff', db.Integer)


class Relations(db.Model):
    __tablename__ = 'relations'

    id = db.Column('id', db.Integer,primary_key=True, autoincrement=True,)
    relation_name = db.Column('relation_name', db.Text)


class Repos(db.Model):
    __tablename__ = 'repos'

    gh_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)
    # TO-DO


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    login = db.Column('login', db.Text)

    #questions = db.relationship('Questions', secondary='t_q')