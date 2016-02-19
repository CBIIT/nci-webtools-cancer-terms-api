# Append the following to your apache configuration

# RedirectMatch ^/glossaryRest$ /glossaryRest/
# <Location /glossaryRest/>
# ProxyPass http://localhost:9900/glossaryRest/
# </Location>

from flask import Flask, request
from socket import gethostname
import sqlite3
import json

app = Flask(__name__)
app.config['db'] = 'glossary.db'

@app.route('/glossaryRest/define', methods = ['POST'])
def define():
    term = json.loads(request.stream.read())['term']
    results = query(term)
    
    if results:
        return json.dumps(results)
    
    return json.dumps([])

def query(term):
    conn = sqlite3.connect(app.config['db'])
    term = ('%' + term + '%',)

    c = conn.cursor()
    c.execute('select * from terms where name like ?', term)
    results = c.fetchall()
    conn.close()

    return results
    
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="port_number", default="9900", help="Sets the Port") 
    args = parser.parse_args()
    port_num = int(args.port_number)

    hostname =  gethostname()
    app.run(host='0.0.0.0', port=port_num, debug = True)
    
