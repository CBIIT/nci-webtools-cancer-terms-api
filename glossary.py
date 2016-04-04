from pysqlcipher import dbapi2 as sqlcipher
from flask import Flask, request
import sqlite3
import json
import os

app = Flask(__name__)
app.config['db'] = 'glossary.db'
app.config['key'] = 'passphrase'


#####################################################################
# Allows a user to query the database for a specific term
# Parameters - 1. User Query
#              2. Search Type:
#                 1. 'contains' - The term name contains the query
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################

@app.route('/glossaryRest/defineCDR', methods = ['POST'])
def define():
    data = json.loads(request.stream.read())
    results = queryCDR(data)
    
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

@app.route('/glossaryRest/define', methods = ['POST'])
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
# Returns the contents of the keyfile
# Parameter - Path to the keyfile
#####################################################################

def loadKey(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as k:
            key = k.read().strip()
            if key:
                app.config['key'] = key

    

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
    parser.add_argument('-p', dest = 'port_number', default = '9080', help = 'Sets the Port')
    parser.add_argument('-k', dest = 'keyfile', default = 'keyfile', help = 'Sets the Keyfile')
    args = parser.parse_args()

    port_num = int(args.port_number)
    loadKey(args.secret_key)

    app.run(host='0.0.0.0', port = port_num, debug = False, use_evalex = False)
    

