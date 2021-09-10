import datetime
import sqlite3

from flask import Flask, g, render_template

app = Flask(__name__)

def db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect('spaz.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    qy = 'select * from things order by utc desc'
    xs = db().cursor().execute(qy).fetchall()
    things = []
    for x in xs:
        x = dict(x)
        x['utc'] = datetime.datetime.fromtimestamp(x['utc'])
        x['url1'] = x['url'].replace('https://', '').replace('www.', '')
        x['url1'] = x['url1'].split('?')[0]
        things.append(x)
    return render_template('home.html', things=things)
