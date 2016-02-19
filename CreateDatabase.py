import xml.etree.ElementTree as et
import sqlite3
import os

# Example usage: writeDictionary('GlossaryTerm', 'dictionary.js')

def loadXML(filename):
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
    if os.path.isfile(dbname):
        os.remove(dbname)

    conn = sqlite3.connect(dbname)
    
    c = conn.cursor()
    c.execute('create table terms(id text, name text, definition text)')
    
    for term in generateDictionary(directory):
        if (term):
            c.execute('insert into terms values (?, ?, ?)', (term['id'], term['TermName'], term['DefinitionText']))
    
    conn.commit()
    conn.close()

def queryDictionary(dbname, term):
    conn = sqlite3.connect(dbname)
    term = ('%' + term + '%',)

    c = conn.cursor()
    c.execute('select * from terms where name like ?', term)
    results = c.fetchall()
    conn.close()

    return results
