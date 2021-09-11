import datetime
import sqlite3

from flask import Flask, g, render_template

app = Flask(__name__)

def db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect('temoc.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

def strip(x, *args):
    for y in args: 
        x = x.replace(y, '') 
    return x

@app.route('/')
def home():
    qy = 'select * from things order by utc desc'
    ys, xs = [], db().cursor().execute(qy).fetchall()
    for x in (dict(x) for x in xs):
        x['utc'] = datetime.datetime.fromtimestamp(x['utc'])
        x['url1'] = strip(x['url'], 'http://', 'https://', 'www.')
        id, site = x['id'], x['site']
        if site == 'hn': x['href'] = f'https://news.ycombinator.com/item?id={id}'
        elif site == 'lobsters': x['href'] = id
        else: x['href'] = f'https://old.reddit.com/{site}/comments/{id}'
        ys.append(x)
    return render_template('home.html', things=ys)
