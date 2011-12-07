(function( $ ){
    
    $.fn.toggle = function( method ) {
        return this.each(function() {
            if (method == 'bind') {
                var $children = $(this).children();
                $children.each(function() {
                    $(this).bind('click.toggle', function() { // Child X was clicked.
                        $children.each(function() { // Show everyone.
                            $(this).removeClass('hidden');
                        });
                        $(this).addClass('hidden'); // Hide X
                    });
                });
            } else if (method == 'unbind') {
                $('*').unbind('.toggle');
            }
        });
    };
})( jQuery );