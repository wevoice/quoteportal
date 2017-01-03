if (typeof django != 'undefined') {
    (function ($) {
    "use strict";

        function toggle_collapsed_inlines(evt) {
            if (this.tagName == 'H2') // Title Bar
                var elem = $(this).find('a.inline_collapse-toggle');
            else // Link
                var elem = $(this);

            if (elem.html() == '(' + gettext('Show') + ')')
                var filter = '.collapsed';
            else
                var filter = ':visible';

            var children = $(elem.parent('h2').nextAll(filter));

            children.each(function(){
                var child = $(this);
                if (!child.hasClass('collapsed'))
                {
                    child.addClass('collapsed');
                    elem.html('(' + gettext('Show') + ')');
                }
                else
                {
                    child.removeClass('collapsed');
                    elem.html('(' + gettext('Hide') + ')');
                }
            });
            $(elem.parent('h2').nextAll('.add-row')).toggle();
            return false;
        }

        django.jQuery(function($) {
            $('div.inline-group').each(function() {
                var h2 = $(this).find('h2:first');
                var children = $(h2.nextAll(':visible'));
                var text = 'Show';

                // Don't collapse if inline contains errors
                children.each(function(){
                    var child = $(this);
                    if (child.find('ul').hasClass('errorlist')) {
                        child.removeClass('collapsed');
                        text = 'Hide';
                    }
                    else {
                        child.addClass('collapsed');
                        text = 'Show';
                    }
                });

                h2.append(' <a class="inline_collapse-toggle collapse-toggle" href="#">(' + gettext(text) + ')</a>');

                h2.find('a.inline_collapse-toggle').bind("click", toggle_collapsed_inlines).removeAttr('href').css('cursor', 'pointer');
                h2.bind("click", toggle_collapsed_inlines).css('cursor', 'pointer');
            });
        });
    })(django.jQuery);
}
