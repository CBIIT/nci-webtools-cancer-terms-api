# nci-analysis-tools-glossary
REST service for glossary of cancer terms

Sample (using JQuery)

```javascript
var query = { 
  term: 'cancer', 
  type: 'contains' // can be 'begins' or 'exact'
};

$.post('http://analysistools-sandbox.nci.nih.gov/glossaryRest/define', 
JSON.stringify(query))
.done(function(data) {
    console.log(data);
});
```
