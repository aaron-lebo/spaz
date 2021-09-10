import sqlite3
import time

import requests

subs = 'news worldnews'.split()

con = sqlite3.connect('spaz.db')
cur = con.cursor()
try:
    cur.execute('create table things(site, id, utc timestamp, title, url)')
except sqlite3.OperationalError:
    pass

while 1:
    ids = cur.execute(f'select id from things where site = "hn"').fetchall()
    ids1 = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()
    for id in set(ids1).difference(set(int(x[0]) for x in ids)):
        x = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{id}.json').json()
        x = ['hn', id, x['time'], x['title'], x.get('url', f'https://news.ycombinator.com/item?id={id}')]
        cur.execute('insert into things values (?, ?, ?, ?, ?)', x)
        con.commit()
        time.sleep(1)

    ids = {x[0] for x in cur.execute(f'select id from things where site != "hn"').fetchall()}
    for sub in subs:
        r = requests.get(f'https://www.reddit.com/r/{sub}.json', headers={'User-agent': 'spaz 0.1'})
        for x in [x['data'] for x in r.json()['data']['children']]:
            if not x['id'] in ids:
                x = [f'r/{sub}', x['id'], x['created_utc'], x['title'], x['url']]
                cur.execute('insert into things values (?, ?, ?, ?, ?)', x)
                con.commit()
        time.sleep(1)
    time.sleep(90)
