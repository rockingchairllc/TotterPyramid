(function( $ ){
    
    $.fn.default = function( method ) {
        return this.each(function() {
            var $this = $(this);
            // Method calling logic
            if ( method == 'bind') {
                var def = $this.val();
                $this.data('default_value.default', def);
                $this.bind('click.default', function() {
                    if ($this.val() == def)
                        $this.val('');
                });
                $this.bind('blur.default', function() {
                    if ($this.val().trim().length == 0)
                        $this.val(def);
                });
            } else if (method == 'unbind') {
                $('*').unbind('.default');
                $('*').removeData('.default');
            } else {
                $this.val($this.data('default_value.default'));
            }
        });
    };
})( jQuery );