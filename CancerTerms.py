# -*- coding: utf-8 -*-

from pysqlcipher import dbapi2 as sqlcipher
from flask import Flask, request
from StringIO import StringIO
import json

app = Flask(__name__)
app.config['DB'] = 'glossary.db'
app.config['KEY'] = open('config.ini').read()
app_db = None


#####################################################################
# Allows a user to query the database for a specific term
#
# Sample queries: curl -G "localhost:10000/cancer/"
#                 curl -G "localhost:10000/term/cancer/"
#                 curl -G "localhost:10000/term/cancer%20vaccine/"
#                 curl -G "localhost:10000/term/contains/cancer/"
#                 curl -G "localhost:10000/term/starts_with/cancer/"
#                 curl -G "localhost:10000/id/CDR0000045333/"
#                 curl -G "localhost:10000/id/contains/45333/"
#                 curl -G "localhost:10000/definition/contains/cancer/"
#
# Parameters - 1. User Query
#
#              2. Database Column:
#                 1. 'id'          - Search by cdr id
#                 2. 'term'        - Search by term name
#                 3. 'definition'  - Search by definition
#
#              3. Search Type:
#                 1. 'contains'    - The term contains the query
#                 2. 'starts_with' - The term begins with the query
#                 3. 'matches'     - The term matches the query
#
#####################################################################

@app.route('/<query>/', methods = ['GET'])
def term(query):
    return json.dumps(lookup('term', None, query))

@app.route('/<column>/<query>/', methods = ['GET'])
def match(column, query):
    return json.dumps(lookup(column, None, query))

@app.route('/<column>/<type>/<query>/', methods = ['GET'])
def define(column, type, query):
    return json.dumps(lookup(column, type, query))



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
# Queries the glossary database
#
# Parameters - 1. Database Column:
#                 1. 'id'          - Search by cdr id
#                 2. 'name'        - Search by term name
#                 3. 'definition'  - Search by definition
#
#
#              2. Search Type:
#                 1. 'contains'    - The term contains the query
#                 2. 'starts_with' - The term begins with the query
#                 3. 'matches'     - The term matches the query
#
#              3. User Query
#
#####################################################################

def lookup(column, type, query):
    if type == 'contains':
        query = '%' + query + '%'
    
    elif type == 'starts_with':
        query += '%'

    if (column in ['id', 'term', 'definition']):
        return app_db.execute(
            'select * from terms where {} like ?'
            .format(column), (query,)).fetchall()

    return



#####################################################################
# Loads database into memory to reduce disk access
#####################################################################

def init_db():
    # Initialize in-memory database
    app_db = sqlcipher.connect(':memory:', check_same_thread = False)

    # Connect to disk-based database and use key
    db = sqlcipher.connect(app.config['DB'])
    db.executescript('pragma key = "{}"'.format(app.config['KEY']))

    # Copy database to memory
    app_db.executescript(''.join(line for line in db.iterdump()))

    return app_db

# Use in-memory database
app_db = init_db()



# For local development only
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 10000, use_debugger = True, use_reloader = True)
