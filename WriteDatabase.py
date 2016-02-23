from pysqlcipher import dbapi2 as sqlcipher
import xml.etree.cElementTree as et
import sqlite3
import time
import os

# Example usage: writeDictionary('GlossaryTerm', 'dictionary.js')
# Test Passphrase - load from external configuration in production
key = 'passphrase'


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

    return term
    
def generateDictionary(directory):
    terms = []

    os.chdir(directory)
    for file in os.listdir('.'):
        terms.append(loadXML(file))
    os.chdir('..')

    return terms

def writeDictionary(directory, dbname):
    init = time.time()

    if os.path.isfile(dbname):
        os.remove(dbname)

    db = sqlite3.connect(dbname)
    db.execute('create table terms(id text, name text, definition text)')
    
    for term in generateDictionary(directory):
        if (term):
            db.execute('insert into terms values (?, ?, ?)', (term['id'], term['TermName'], term['DefinitionText']))
    
    db.commit()
    db.close()
    
    print 'Time required to create non-encrypted database: ' + str(time.time() - init)


def queryDictionary(dbname, term):
    db = sqlite3.connect(dbname)
    term = ('%' + term + '%',)

    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results
    
    
def writeEncryptedDictionary(directory, dbname):
    init = time.time()

    if os.path.isfile(dbname):
        os.remove(dbname)

    db = sqlcipher.connect(dbname)
    db.executescript('pragma key="' + key + '"')
    db.execute('create table terms(id text, name text, definition text)')
    
    for term in generateDictionary(directory):
        if (term):
            db.executescript('pragma key="' + key + '"')
            db.execute('insert into terms values (?, ?, ?)', (term['id'], term['TermName'], term['DefinitionText']))
    
    db.commit()
    db.close()
    
    print 'Time required to create encrypted database: ' + str(time.time() - init)

def queryEncryptedDictionary(dbname, term):
    db = sqlcipher.connect(dbname)
    term = ('%' + term + '%',)

    db.executescript('pragma key="' + key + '"')
    results = db.execute('select * from terms where name like ?', term).fetchall()
    db.close()

    return results