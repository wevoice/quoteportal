if (typeof django != 'undefined') {
    (function($) {
        "use strict";

        $(function() {
            var form = $('#changelist-form');
            var inputs = $('#changelist-form input, #changelist-form select, #changelist-form textarea')  // all inputs
                .not('.action-select,#action-toggle,[name=action]')  // but not those specific to the admin
                .not('[type=hidden],[type=submit]');  // nor the hidden inputs or the submit button

            $('#changelist-form [name=_save]').hide();

            function form_ajax_submit() {
                var data = form.serialize();
                data += '&_save=1';  // add the submit button
                $.post(form.attr('action'), data, display_message_from_answer);
            }

            function display_message_from_answer(answer) {
                $('.messagelist').remove();
                $('.breadcrumbs').after($(answer).find('.messagelist').fadeIn());
                $('.field-total_words').each(function( index ) {
                    this.innerHTML = $(answer).find('.field-total_words')[index].innerHTML;
                });
                $('.field-ost_elements').each(function( index ) {
                    this.innerHTML = $(answer).find('.field-ost_elements')[index].innerHTML;
                });
            }

            inputs.change(function() {
                form_ajax_submit();
            });
        });
    })(django.jQuery);
}