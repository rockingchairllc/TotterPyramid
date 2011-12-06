/*
 * Autoresize textarea for Jeditable
 *
 * Copyright (c) 2008 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 * 
 * Depends on Autogrow jQuery plugin by Chrys Bader:
 *   http://www.aclevercookie.com/facebook-like-auto-growing-textarea/
 *
 * Project home:
 *   http://www.appelsiini.net/projects/jeditable
 *
 * Revision: $Id$
 *
 */
 
$.editable.addInputType('autoResize', {
    element : function(settings, original) {
        var textarea = $('<textarea />');
        $(this).append(textarea);
        return(textarea);
    },
    plugin : function(settings, original) {
        $('textarea', this).autoResize(settings.autoResize);
    }
});