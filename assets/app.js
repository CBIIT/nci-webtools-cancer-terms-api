var termNames = [];


$(document).ready(function() {
    
    retrieveTermNames();
    
    $("#term").keypress(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            submit();
        }
    });
    
    $('#search').click(submit);
    $('#submitText').click(processModule.processText);
});

function submit() {
    var term = DOMPurify.sanitize($('#term').val());
    
    if (term) {
        $('#term').val('Please Wait...');
        $('#term').attr('disabled', true);
        $('#search').attr('disabled', true);
        
        var request = $.post('http://' + window.location.hostname + '/glossaryRest/define', 
        JSON.stringify({ term: term, type: 'contains' }))

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

var processModule = (function() {
    var enteredText = '';
    var processedText = '';
    
    return {
        processText: processText
    };
    
    function processText() {
        processedText = '';
        
        var text = $('#sampleText').val().split(' ');
        var html = '';
        console.log(text);
        
        for (var i = 0; i < text.length; i ++)
            makeRequest(text[i]);
        
    }


    function makeRequest(term) {
    
        if ($.inArray(term, termNames)) { 
    
            var request = $.post('http://' + window.location.hostname + '/glossaryRest/define', 
            JSON.stringify({ term: term, type: 'exact' }))

            request.done(function(data) {
                data = JSON.parse(data);
                
                console.log(data);
                
                if (data.length > 0) {
                    console.log(term, data);
                    processedText += '<a href="#" data-toggle="tooltip" data-placement="top" title="' + data[0][2] + '">' + term + '</a> '
                }
                
                else {
                    console.log(term, ' no data' );
                    processedText += term + ' ';
                }
                
                console.log(processedText);
                
                $('#processedText').html(processedText);
            });
        }
    }
})();


function retrieveTermNames() {
    $.post('http://' + window.location.hostname + '/glossaryRest/define', 
    JSON.stringify({ term: '%', type: 'contains' }), function(data) {
        console.log('Retrieved term names');
        termNames = JSON.parse(data).map(function(term) { 
            return term[1]; });
    });
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
