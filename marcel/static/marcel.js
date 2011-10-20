// Javascript code for Marcel. Requires jQuery >= 1.4.3
//
//  :copyright: (c) 2011 by Ori Livneh
//  :license: GPLv3, see LICENSE for more details.
(function ($) {
    $(document).ready(function() {
        // Fade out any alerts after a delay
        $('.flash-message').delay(1000).fadeOut('slow');

        // Expand/contract entries by clicking on the headline
        $('article header').click(function() {
            $('article header').not(this).next().slideUp();
            $(this).next().slideToggle();
        });
    });
}(jQuery));
