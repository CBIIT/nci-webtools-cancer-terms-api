# nci-analysis-tools-glossary
RESTful service for glossary of cancer terms

Search by term (using JQuery)
```javascript
var query = { 
  term: 'cancer', 
  type: 'contains' // can be 'begins' or 'exact'
};

$.post('http://analysistools-dev.nci.nih.gov/glossaryRest/define', 
JSON.stringify(query))
.done(function(data) {
    console.log(data);
});
```

Search by CDR
```javascript
var query = { 
  id: 'CDR0000045333', 
};

$.post('http://analysistools-dev.nci.nih.gov/glossaryRest/defineCDR', 
JSON.stringify(query))
.done(function(data) {
    console.log(data);
});
```
