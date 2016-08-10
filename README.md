####RESTful service for glossary of cancer terms

#####Usage:
```javascript

// if match type is not specified, 'exact' will be used
GET http://analysistools-dev.nci.nih.gov/CancerTerms/<id|name|definition>/?query=<query>&type=<exact|begins|contains>
```

#####Examples:
```javascript

// search for the term with cdr id: CDR0000045333
GET http://analysistools-dev.nci.nih.gov/CancerTerms/id/?query=CDR0000045333

// search for 'cancer' - exact matches only
GET http://analysistools-dev.nci.nih.gov/CancerTerms/name/?query=cancer

// search for terms that contain 'cancer' as a part of their names
GET http://analysistools-dev.nci.nih.gov/CancerTerms/name/?query=cancer&type=contains

// search for terms with definitions that contain 'cancer' - search type defaults to 'contains' for definitions
GET http://analysistools-dev.nci.nih.gov/CancerTerms/definition/?query=cancer
```

#####Examples using jQuery:
```javascript
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/id', {query: 'CDR0000045333'}, console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/name', {query: 'cancer'}, console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/name', {query: 'cancer', type: 'contains'}, console.log)
$.get('http://analysistools-dev.nci.nih.gov/CancerTerms/definition', {query: 'cancer'}, console.log)
```
