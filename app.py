import datetime
import sqlite3

from flask import Flask, g, redirect, render_template, request

app = Flask(__name__)

def db():
    db = getattr(g, '_db', None)
    if not db:
        db = g._db = sqlite3.connect('temoc.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, '_db', None)
    if db:
        db.close()

def strip(x, *args):
    for y in args: 
        x = x.replace(y, '') 
    return x

@app.route('/')
def home():
    qy = 'select * from things where save = 0 and hide = 0 order by utc desc'
    ys, xs = [], db().cursor().execute(qy).fetchall()
    for x in (dict(x) for x in xs):
        x['utc'] = datetime.datetime.fromtimestamp(x['utc'])
        x['url1'] = strip(x['url'], 'http://', 'https://', 'www.')
        dom = x['url1'].split('/')
        x['dom'] = dom[0], '/'.join(dom[1:])
        id, site = x['id'], x['site']
        if site == 'hn': 
            x['href'] = f'https://news.ycombinator.com/item?id={id}'
        elif site == 'lobsters': 
            x['href'] = f'https://lobste.rs/s/{id}'
        else: 
            x['href'] = f'https://old.reddit.com/{site}/{id}'
        ys.append(x)
    return render_template('home.html', things=ys)

@app.route('/things/<id>', methods=['post'])
def things(id):
    f = request.form
    for x in ['save', 'hide']:
        if f.get(x, None) is not None:
            d, qy = db(), f'update things set {x} = 1 where site = ? and id = ?'
            d.cursor().execute(qy, (f['site'], id))
            d.commit()
    return redirect('/')
