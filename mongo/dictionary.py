# Append the following to your apache configuration

# RedirectMatch ^/dictionaryRest$ /dictionaryRest/
# <Location /dictionaryRest/>
# ProxyPass http://localhost:9900/dictionaryRest/
# </Location>


from flask import Flask, request
from socket import gethostname
import pymongo
import json

app = Flask(__name__)

client = MongoClient()

# update this reference
db = client.definitions_database

@app.route('/dictionaryRest/define', methods = ['GET'])
def define():
    if 'term' in request.args:
    
        termName = request.args['termName']
        terms = []
        
        # update query to reflect actual database
        results = db.definitions.find({ 'name': '/' + termName +  '/' })
        
        for result in results:
            term['termName'] = result['termName']
            term['definition'] = result['definition']
            terms.append(term)
        
        return json.dumps(terms)
    
    else:
        return 'Correct parameter not provided in GET'

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="port_number", default="9900", help="Sets the Port") 
    args = parser.parse_args()
    port_num = int(args.port_number)

    hostname =  gethostname()
    app.run(host='0.0.0.0', port=port_num, debug = True)
    