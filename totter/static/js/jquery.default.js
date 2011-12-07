(function( $ ){
    
    $.fn.default = function( method ) {
        return this.each(function() {
            var $this = $(this);
            // Method calling logic
            if ( method == 'bind') {
                var def = $this.val();
                $this.data('default_value', def);
                $this.click(function() {
                    if ($this.val() == def)
                        $this.val('');
                });
                $this.blur(function() {
                    if ($this.val().trim().length == 0)
                        $this.val(def);
                });
            } else {
                $this.val($this.data('default_value'));
            }
        });
    };
})( jQuery );