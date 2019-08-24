# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import unicodedata


# connect to database
db = TinyDB('db.json')
gigs = db.table('gigs')
Gig = Query()


def u(x):
    return unicode(x).encode('utf8')


for row in gigs:
    print(row)

