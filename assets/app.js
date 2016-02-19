$(document).ready(function() {
    
    $("#term").keypress(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            submit();
        }
    });
    
    $('#search').click(submit);
});

function submit() {
    var term = DOMPurify.sanitize($('#term').val());
    
    if (term) {
        $('#term').val('Please Wait...');
        $('#term').attr('disabled', true);
        $('#search').attr('disabled', true);
        
        var request = $.post('http://' + window.location.hostname + '/glossaryRest/define', JSON.stringify({ term: term }))

        request.done(function(data) {
            console.log(data);
            updateResults(term, JSON.parse(data));
        });
        
        request.fail(function() {
            console.log('Service is not available');
            
            // if service is not available, use sample data
            updateResults(term, [
                ['Sample ID', 'Sample Term', 'Sample Definition']
            ]);
        });
    }    
}

function updateResults(term, results) {
    var resultsHTML = '';
    results.forEach(function(result) {
        resultsHTML += 
        '<div class="result">' + 
        '<h4 class="resultHeader">' + result[1] + '</h4>' +
        '<p>' + result[2] + '</p>' +
        '</div>';
    });
    
    $('#resultsFound').html(results.length + ' results found for: ' + term);
    $('#results').html(resultsHTML);
    
    $('#search').attr('disabled', false);
    $('#term').attr('disabled', false);
    $('#term').val('');
}
