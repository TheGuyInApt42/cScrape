# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import unicodedata
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



    

g = gigs.search(Gig.c_id == '6963468857')
#g = gigs.search(Gig.c_id == '6951796322')
'''
for el in g:
    try:
        print(el['description'].encode('utf-8', errors='replace').decode('cp1252'))
    except UnicodeDecodeError:
        print(el['description'])
    except:
        print('error')
'''  

for row in gigs:
    try:
        print(row['description'].encode('utf-8', errors='replace').decode('cp1252'))
    except UnicodeDecodeError:
        print(row['description'])
    except:
        print('error')

# print('\u2605'.encode('utf-8', errors='replace').decode('cp1252'))
