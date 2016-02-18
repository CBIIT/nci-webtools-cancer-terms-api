$(document).ready(function() {
    $('#search').click(function() {
        
        var term = DOMPurify.sanitize($('#term').val());
        
        if (term) {
            $('#term').val('Please Wait...');
            $('#term').attr('disabled', true);
            $('#search').attr('disabled', true);
            
            var request = $.get('http://' + window.location.hostname + '/dictionaryRest/define', { term: term })

            request.done(function(data) {
                updateResults(term, JSON.parse(data));
            });
            
            request.fail(function() {
                console.log('Service is not available');
                
                // if service is not available, use sample data
                updateResults(term, [
                    {
                        'termName' : 'sample term',
                        'definition' : 'Sample definition'
                    },
                    {
                        'termName' : 'sample term 2',
                        'definition' : 'Sample definition 2'
                    },
                    {
                        'termName' : 'sample term 3',
                        'definition' : 'Sample definition 3'
                    }
                ]);
            });
        }
    });
});

function updateResults(term, results) {
    var resultsHTML = '';
    results.forEach(function(result) {
        resultsHTML += 
        '<div class="result">' + 
        '<h4 class="resultHeader">' + result.termName + '</h4>' +
        '<p>' + result.definition + '</p>' +
        '</div>';
    });
    
    $('#resultsFound').html(results.length + ' results found for: ' + term);
    $('#results').html(resultsHTML);
    
    $('#search').attr('disabled', false);
    $('#term').attr('disabled', false);
    $('#term').val('');
}
