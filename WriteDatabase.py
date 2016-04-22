#!/usr/bin/python

from pysqlcipher import dbapi2 as sqlcipher
import xml.etree.cElementTree as et
import sqlite3
import zipfile
import sys
import os

# Example usage: 
# python WriteDatabase.py -d GlossaryTerm -k secretKey -o glossary.db

config = {'key': 'passphrase'}

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

            return (term['id'], term['TermName'], term['DefinitionText'])



#####################################################################
# Returns the contents of a directory as an array of glossary terms
# Parameter - Path to the glossary terms directory
#####################################################################

def generateDictionary(directory):
    terms = []

    os.chdir(directory)

    files = os.listdir('.')
    for index, file in enumerate(files):
        print 'Reading xml documents ({0}/{1})\r'.format(index + 1, len(files)),
        sys.stdout.flush()

        term = loadXML(file)

        if term:
            terms.append(term)

    print
    os.chdir('..')
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
    db.executescript('pragma key = "%s" ' % config['key'])
    db.execute('create table terms(id text, name text, definition text)')
    
    terms = generateDictionary(directory)
    for index, term in enumerate(terms):
        print 'Adding terms ({0}/{1})\r'.format(index + 1, len(terms)),
        sys.stdout.flush()
        
        db.executescript('pragma key = "%s" ' % config['key'])
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

def queryDatabase(dbname, term, type = 'exact'):
    db = sqlcipher.connect(dbname)

    if type == 'contains':
        term = '%' + term + '%'
        
    elif type == 'begins':
        term += '%'

    term = tuple([term])
    db.executescript('pragma key = "%s" ' % config['key'])
    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results


    
#####################################################################
# Generates a glossary database from a specified folder
# Parameters - 1. -d, --directory   The folder to read terms from
#              2. -k, --keyfile     The file containing the secret key
#              2. -o, --output      The name of the output file
#####################################################################

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Creates an encrypted sqlite3 database of terms from a given directory')
    parser.add_argument('-d', '--directory', dest = 'directory', default='GlossaryTerm', help='Sets the glossary terms directory')
    parser.add_argument('-k', '--keyfile', dest = 'keyfile', default='keyfile', help='Sets the keyfile to read from')
    parser.add_argument('-o', '--output', dest = 'output', default='glossary.db', help='Sets the name of the output file')
    args = parser.parse_args()

    if os.path.isfile(args.keyfile):
        print 'Loading keyfile: {0}'.format(args.keyfile)
        with open(args.keyfile, 'r') as f:
            key = f.read.strip()
            if key:
                config['key'] = key
    else
        print 'Warning: Keyfile {0} not found. Using default value for passphrase'.format(args.keyfile)
 

    if not os.path.isdir(args.directory):
        print 'Warning: {0} is not a valid directory, using default directory: GlossaryTerm'.format(args.directory)
        args.directory = 'GlossaryTerm'
	    
        if not os.path.isDir('GlossaryTerm'):
            filename = 'GlossaryTerm.zip'
            print 'Extracting glossary terms from archive: {0}'.format(filename)
            zip = zipfile.ZipFile(filename)
            zip.extractall()
            zip.close()

    createDatabase(args.directory, args.output)
