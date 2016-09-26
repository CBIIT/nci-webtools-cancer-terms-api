####RESTful service for glossary of cancer terms

#####Usage:
```javascript

// if match type is not specified, 'exact' will be used
GET http://analysistools-dev.nci.nih.gov/CancerTerms/<id|term|definition>/<begins_with|contains|matches>/<query>
```

#####Examples:
```javascript

// search for 'cancer' - exact matches only
GET http://analysistools-dev.nci.nih.gov/CancerTerms/cancer

// search by cdr id: CDR0000045333
GET http://analysistools-dev.nci.nih.gov/CancerTerms/id/CDR0000045333

// search for terms that contain 'cancer' as a part of their names
GET http://analysistools-dev.nci.nih.gov/CancerTerms/term/contains/cancer

// search for terms with definitions that contain 'cancer'
GET http://analysistools-dev.nci.nih.gov/CancerTerms/definition/contains/cancer
```

#####Examples using jQuery:
```javascript
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/id/CDR0000045333', console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/term/cancer', console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/term/cancer vaccine', console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/definition/contains/cancer', console.log)
```
