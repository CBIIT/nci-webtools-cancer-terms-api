#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from pysqlcipher import dbapi2 as sqlcipher
import (
    xml.etree.cElementTree as et,
    os,
    sqlite3,
    sys,
    uuid)

# Example usage: 
# python WriteDatabase.py -i CancerTerms

config = {
    DB = 'glossary.py',
    KEY = uuid.uuid4().hex
}

with open('config.ini', 'w') as f:
    f.write(config.KEY)


#####################################################################
# Returns the contents of a single XML document as a tuple
# Parameter - Path to the XML document
#####################################################################

def loadXML(filename):
    if not filename.endswith('.xml'):
        return
    
    root = et.parse(filename).getroot()
    term = {'id': root.attrib['id']}
    term['TermName'] = root.find('TermName').text

    for child in root.findall('TermDefinition'):
        audience = child.find('Audience')
        dictionary = child.find('Dictionary')
        
        if (audience.text == 'Patient') or \
           (dictionary and dictionary.text == 'Cancer.gov'):

            definition = child.find('DefinitionText')
            text = definition.text if definition.text else ''
            
            for subchild in definition:
                text += subchild.text + subchild.tail if subchild.tail else ''
                
            term['DefinitionText'] = ' '.join(text.replace('\n', '').split())


            if (type(term['DefinitionText']) == unicode):
                term['DefinitionText'] = term['DefinitionText'].encode('ascii', 'xmlcharrefreplace')

            return (term['id'], term['TermName'], term['DefinitionText'])



#####################################################################
# Returns the contents of a directory as an array of glossary terms
# Parameter - Path to the glossary terms directory
#####################################################################

def generateDictionary(directory):
    terms = []

    files = os.listdir(directory)
    for index, file in enumerate(files):
        print 'Reading xml documents ({0}/{1})\r'.format(index + 1, len(files)),
        sys.stdout.flush()

        term = loadXML(os.path.join(directory, file))

        if term:
            terms.append(term)

    print

    return terms



#####################################################################
# Creates an encrypted glossary database from a directory
# Parameters - 1. Path to the glossary terms directory
#              2. Path to the generated database file
#####################################################################

def createDatabase(directory, dbname):
    
    if os.path.isfile(dbname):
        print 'Replacing existing database: {0}'.format(dbname)
        os.remove(dbname)

    db = sqlcipher.connect(dbname)
    db.executescript('pragma key = "%s" ' % config['KEY'])
    db.execute('create table terms(id text, term text, definition text)')
    
    terms = generateDictionary(directory)
    for index, term in enumerate(terms):
        print 'Adding terms ({0}/{1})\r'.format(index + 1, len(terms)),
        sys.stdout.flush()
        
        db.executescript('pragma key = "{0}"'.format(config['KEY']))
        db.execute('insert into terms values (?, ?, ?)', term)

    db.commit()
    db.close()
    
    print 'Finished writing database: {0}'.format(dbname)



#####################################################################
# Queries an encrypted glossary database
# Parameters - 1. Path to the database
#              2. User Query
#              3. Search Type:
#                 1. 'contains' - The term name contains the query
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################

def query(dbname, column, term, type = 'exact'):

    # return empty array if invalid column was supplied
    if (not column in ['id', 'term', 'definition']):
        return []
    
    db = sqlcipher.connect(dbname)
    
    if type == 'contains':
        term = '%' + term + '%'
    
    elif type == 'begins_with':
        term += '%'
    
    db.executescript('pragma key = "{0}"'.format(config['KEY']))

    results = db.execute(
        'select * from terms where {0} like ?'.format(column), 
        tuple([term])
    ).fetchall()
    
    db.close()
    
    return results



################################################################################
# Generates a glossary database from a specified archive
#
# Parameters
#             -i, --input     The path to the directory containing xml terms
#             -o, --output    The path to the output file (default: glossary.db)
################################################################################

import argparse
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description = '''Creates an encrypted sqlite3 database from a directory
                         containing xml terms'''
    )
    
    parser.add_argument(
        '-i', '--input', 
        dest    = 'input', 
        default = 'GlossaryTerm', 
        help    = 'Sets the directory containing xml terms'
    )
    
    parser.add_argument(
        '-o', '--output', 
        dest    = 'output', 
        default = config['DB'], 
        help    = 'Sets the output filename'
    )
    
    args = parser.parse_args()
    createDatabase(args.input, args.output)
