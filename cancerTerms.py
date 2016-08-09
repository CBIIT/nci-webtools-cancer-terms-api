from pysqlcipher import dbapi2 as sqlcipher
from flask import Flask, request
from StringIO import StringIO
import json

app = Flask(__name__)

# Configuration for ['DB', 'KEY']
app.config.from_pyfile('config.ini')
app_db = None


#####################################################################
# Sample query: curl "localhost:9000/name/?query=cancer"
#
# Allows a user to query the database for a specific term
# Parameters - 1. User Query
#
#              2. Database Column:
#                 1. 'id'         - Search by cdr
#                 2. 'name'       - Search by term name
#                 3. 'definition' - Search by definition
#
#              3. Search Type:
#                 1. 'contains'   - The term contains the query
#                 2. 'begins'     - The term begins with the query
#                 3. 'exact'      - The term matches the query
#
#####################################################################

@app.route('/<column>/', methods = ['GET'])
def define(column):
    query = request.args.get('query')
    type  = request.args.get('type')

    return json.dumps(lookup(query, column, type))



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
# Queries an encrypted glossary database
# Parameters - 1. User Query
#
#              2. Database Column:
#                 1. 'id'         - Search by cdr
#                 2. 'name'       - Search by term name
#                 3. 'definition' - Search by definition
#
#
#              3. Search Type:
#                 1. 'contains'   - The term contains the query
#                 2. 'begins'     - The term begins with the query
#                 3. 'exact'      - The term matches the query
#####################################################################

def lookup(query, column = 'name', type = 'exact'):
    if type == 'contains':
        query = '%' + query + '%'
    
    elif type == 'begins':
        query += '%'

    if (column in ['id', 'name', 'definition']):
        return app_db.execute('select * from terms where {} like ?'.format(column), (query,)).fetchall()

    return



#####################################################################
# Loads database into memory to eliminate disk access
#####################################################################

def init_db(config):
    # Initialize in-memory database
    app_db = sqlcipher.connect(':memory:', check_same_thread = False)

    # Connect to disk-based database and use key
    db = sqlcipher.connect(config['DB'])
    db.executescript('pragma key = "{}"'.format(config['KEY']))

    # Copy database to memory
    app_db.executescript("".join(line for line in db.iterdump()))

    return app_db

# Use in-memory database
app_db = init_db(app.config)




# For local development only
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 9000, use_debugger = True, use_reloader = True)
