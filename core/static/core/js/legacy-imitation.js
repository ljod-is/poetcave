/*
This CSS file is to imitate the look and feel of the legacy website so that
we can use modern HTML but still retain the old look and feel.

When we get to the design phase, once we're feature-complete with regard to
the old website, this file might be replaced with something completely
different. It still contains some functionality that may be useful in the new
design, whatever it may be.
*/

$(document).ready(function() {
    
    // Buttons with a "href" attribute function as links.
    $('button[href]').click(function() {
        location.href = $(this).attr('href');
    });

});
