from pysqlcipher import dbapi2 as sqlcipher
import xml.etree.cElementTree as et
import sqlite3
import os

# Example usage: createDatabase('GlossaryTerm', 'glossary.db')
# Test Passphrase - load from external configuration in production
key = 'passphrase'

#####################################################################
# Loads the passphrase from a keyfile 
# Parameters - 1. The name of the keyfile
#####################################################################
def loadKey(filename):
    with open('keyfile', 'r') as k:
        key = k.read().strip()


#####################################################################
# Returns the contents of a single xml document as an array 
# Parameters - 1. The filename of the XML document
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
                if (sub.tag == 'Audience' and sub.text != 'Patient') \
                or (sub.tag == 'Dictionary' and sub.text != 'Cancer.gov'):
                    return
                elif sub.tag == 'DefinitionText':
                    term[sub.tag] = sub.text
                        for subchild in sub
                            term[sub.tag] += subchild.text + subchild.tail            
    return term
    

#####################################################################
# Returns the contents of a directory as an array of glossary terms 
# Parameters - 1. The name of the directory containing XML documents
#####################################################################
def generateDictionary(directory):
    terms = []

    os.chdir(directory)
    for file in os.listdir('.'):
        term = loadXML(file)

        if (term):
            terms.append(term)
    
    os.chdir('..')
    return terms
    

#####################################################################
# Creates an encrypted glossary database from a directory
# Parameters - 1. Directory containing XML documents to read
#              2. Name of generated database file
#####################################################################
def createDatabase(directory, dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)

    db = sqlcipher.connect(dbname)
    db.executescript('pragma key="' + key + '"')
    db.execute('create table terms(id text, name text, definition text)')
    
    for term in generateDictionary(directory):
        db.executescript('pragma key="' + key + '"')
        db.execute('insert into terms values (?, ?, ?)', (term['id'], term['TermName'], term['DefinitionText']))
    
    db.commit()
    db.close()


#####################################################################
# Queries an encrypted glossary database
# Parameters - 1. Database filename
#              2. User Query
#              3. Search Type:
#                 1. 'contains' - The term name contains the query 
#                 2. 'begins'   - The term name begins with the query
#                 3. 'exact'    - The term name matches the query
#####################################################################
def queryDatabase(dbname, term, type = 'exact'):
    db = sqlcipher.connect(dbname)
    
    if type == 'contains':
        term = ('%' + term + '%',)

    elif type == 'begins':
        term = (term + '%',)
    
    elif type == 'exact':
        term = (term,)

    db.executescript('pragma key="' + key + '"')
    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results