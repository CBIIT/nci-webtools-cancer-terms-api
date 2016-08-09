from pysqlcipher import dbapi2 as sqlite
from flask import Flask, request
from StringIO import StringIO
import sqlite3
import json
import os

app = Flask(__name__)

# Configuration for: config['DB', 'KEY']
app.config.from_pyfile('config.ini')

db = sqlite.connect(app.config['DB'])




#####################################################################
# Allows a user to query the database for a specific term
# Parameters - 1. User Query
#              2. Search Type:
#                 1. 'contains' - The term name contains the query
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################

@app.route('/defineCDR', methods = ['GET'])
def defineCDR():
    data = json.loads(request.stream.read())
    results = queryCDR(data['cdr'])
    
    if results:
        return json.dumps(results)
    
    return json.dumps([])
    


#####################################################################
# Allows a user to query the database for a specific term
# Parameters - 1. User Query
#              2. Search Type:
#                 1. 'contains' - The term name contains the query
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################

@app.route('/define', methods = ['GET'])
def define():
    data = json.loads(request.stream.read())
    term = data['term']
    type = data['type']
    
    results = query(term, type)
    
    if results:
        return json.dumps(results)
    
    return json.dumps([])
    
    

#####################################################################
# Queries an encrypted glossary database
# Parameters - 1. User Query
#              2. Search Type:
#                 1. 'contains' - The term name contains the query
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################

def query(term, type = 'exact'):
    db = sqlcipher.connect(app.config['db'])

    if type == 'contains':
        term = '%' + term + '%'
    
    elif type == 'begins':
        term += '%'

    term = tuple([term])
    db.executescript('pragma key = "%s" ' % app.config['key'])
    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results
    
    

#####################################################################
# Queries an encrypted glossary database based on the CDR id
# Parameters - 1. User Query
#####################################################################

def queryCDR(id):
    db = sqlcipher.connect(app.config['db'])

    id = tuple([id])
    db.executescript('pragma key = "%s" ' % app.config['key'])
    results = db.execute('select * from terms where id like ?', id).fetchall()
    db.close()

    return results

#####################################################################
# Loads database into memory to reduce disk access
#####################################################################
def init_db(app):
    conn = sqlite3.connect(app.config['DB'])
    temp = StringIO()
    for line in con.iterdump():
        temp.write('%s\n' % line)
    conn.close()
    temp.seek(0)

    app.sqlite = sqlite3.connect(':memory:')
    app.sqlite.cusor().executescript(tempfile.read())
    app.sqlite.commit()
    app.sqlite.row_factory = sqlite3.Row


#####################################################################
# Allows cross-origin resource sharing
#####################################################################

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response



#####################################################################
# Launch the flask application server
# Parameters - 1. -p (Port Number, sandbox: 9080 - dev: 8080)
#              2. -k (Path to keyfile, default: 'keyfile')
#####################################################################

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest = 'port', type = int, default = '8080', help = 'Sets the Port')
    parser.add_argument('-k', dest = 'keyfile', default = 'keyfile', help = 'Sets the Keyfile')
    args = parser.parse_args()

    loadKey(args.keyfile)

    app.run(host='0.0.0.0', port = args.port, debug = False, use_evalex = False)
    

