import xml.etree.ElementTree as et
import json
import os

# Example usage: writeDictionary('GlossaryTerm', 'dictionary.js')

def loadXML(filename):
    root = et.parse(filename).getroot()
    definition = root.attrib

    for child in root:
        if child.tag == 'TermName':
            definition[child.tag] = child.text

        elif child.tag == 'TermDefinition':
            for sub in child:
                if (sub.tag == 'Audience' and sub.text != 'Patient') \
                or (sub.tag == 'Dictionary' and sub.text != 'Cancer.gov'):
                    return
                elif sub.tag == 'DefinitionText':
                    definition[sub.tag] = sub.text

    return definition

def generateDictionary(directory):
    definitions = []

    os.chdir(directory)
    for file in os.listdir('.'):
        definitions.append(loadXML(file))
    os.chdir('..')

    return json.dumps({'terms': definitions})

def writeDictionary(directory, filename):
    contents = 'var data = ' + generateDictionary(directory) + ';'

    file = open(filename, 'w')
    file.write(contents)
    file.close()
    
