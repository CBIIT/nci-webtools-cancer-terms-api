#!/usr/bin/python

from pysqlcipher import dbapi2 as sqlcipher
import xml.etree.cElementTree as et
import sqlite3
import os

# Example usage: createDatabase('GlossaryTerm', 'glossary.db')
# Test Passphrase - load from external configuration in production

key = 'passphrase'
loadKey('keyfile')

#####################################################################
# Loads the passphrase from a keyfile
# Parameter - Path to the keyfile
#####################################################################

def loadKey(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as k:
            key = k.read().strip()



#####################################################################
# Returns the contents of a single XML document as a tuple
# Parameter - Path to the XML document
#####################################################################

def loadXML(filename):
    if not filename.endswith('.xml'):
        return

    root = et.parse(filename).getroot()
    term = root.attrib

    for child in root:
        if child.tag == 'TermName':
            term[child.tag] = child.text
        elif child.tag == 'TermDefinition':

            for sub in child:
                if (sub.tag == 'Audience' and sub.text != 'Patient') or \
                   (sub.tag == 'Dictionary' and sub.text != 'Cancer.gov'):
                    return
                elif sub.tag == 'DefinitionText':
                    term[sub.tag] = sub.text if sub.text else ''
                    for subchild in sub:
                        term[sub.tag] += subchild.text + subchild.tail if subchild.tail else ''

    return (term['id'], term['TermName'], term['DefinitionText'])



#####################################################################
# Returns the contents of a directory as an array of glossary terms
# Parameter - Path to the glossary terms directory
#####################################################################

def generateDictionary(directory):
    terms = []

    os.chdir(directory)
    for file in os.listdir('.'):
        term = loadXML(file)

        if term:
            terms.append(term)

    os.chdir('..')
    return terms



#####################################################################
# Creates an encrypted glossary database from a directory
# Parameters - 1. Path to the glossary terms directory
#              2. Path to the generated database file
#####################################################################

def createDatabase(directory, dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)

    db = sqlcipher.connect(dbname)
    db.executescript('pragma key = "%s" ' % key)
    db.execute('create table terms(id text, name text, definition text)')

    for term in generateDictionary(directory):
        db.executescript('pragma key = "%s" ' % key)
        db.execute('insert into terms values (?, ?, ?)', term)

    db.commit()
    db.close()



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
    db.executescript('pragma key = "%s" ' % key)
    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results
