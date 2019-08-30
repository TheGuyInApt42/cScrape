# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import sys

# connect to database
db = TinyDB('db.json')
gigs = db.table('gigs')
Gig = Query()
test = db.table('test')
Test = Query()



def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def unicode_fix(text):
    new_text = ''
    try:
        new_text = text.encode('utf-8', errors='replace').decode('cp1252')
    except UnicodeDecodeError:
        new_text = text
    except Exception as e:
        print('error is {}'.format(e))
    return new_text


    

g = gigs.search(Gig.post_title == 'Coding and website expertise needed')
t = gigs.get(Gig.c_id == '6946199300')

t['post_title'] = unicode_fix(t['post_title'])
#  print(t['post_title'])

'''
for el in g:
    try:
        print(el['description'].encode('utf-8', errors='replace').decode('cp1252'))
    except UnicodeDecodeError:
        print(el['description'])
    except:
        print('error')
'''


def db_size(db):
    print(len(db))

def print_all(db_table):
    for row in db_table:
        row['post_title'] = unicode_fix(row['post_title'])
        row['description'] = unicode_fix(row['description'])
        print(row.doc_id, row)

print_all(gigs)

