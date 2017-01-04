if (typeof django != 'undefined') {
    (function ($) {

        var form = $('#scoping_form');
        function form_ajax_submit(scopingChange) {
            var data = form.serialize();
            data += '&_save=1';  // add the submit button
            if (!scopingChange){
                data += '&_languageupdate=1';
                $.post(form.attr('action'), data, update_formset_from_response); // Update language forms for pricing table
            }
            if (scopingChange){
                $.post(form.attr('action'), data, update_formset_from_response); // update data for Total Words and OST Elements
                data += '&_languageupdate=1';
                $.post(form.attr('action'), data, update_formset_from_response); // Update language forms for pricing table
            }
        }

        function update_formset_from_response(response) {
            /**
            * @param response
            * @param response.status   status of ajax call returned from server
            * @param response.inline_form   formset row returned in ajax call
            */
            if (response.status == "languages updated!"){
                var current_inlines = $('.tabular.inline-related');
                var response_inlines = $(response.inline_form).find('.tabular.inline-related');
                current_inlines[0].innerHTML = response_inlines[0].innerHTML;
            } else {
                var estimate_url = $(response).find('.messagelist a').attr('href');
                $(response).find('tr').each(function() {
                    var this_url = $(this).find('.field-name a').attr('href');
                    if (this_url == estimate_url){
                        var total_words_field = $('.field-total_words p');
                        total_words_field[0].innerHTML = $(this).find('.field-total_words')[0].innerHTML;
                        total_words_field[1].innerHTML = $(this).find('.field-ost_elements')[0].innerHTML;
                    }
                });
            }
        }

        $('#id_course_play_time, #id_narration_time, #id_embedded_video_time, #id_video_count, #id_transcription, ' +
            '#id_linked_resources').change(function () {
            form_ajax_submit(true);
        });

        $(document).off('change');
        $(document).on('change', '[id^=id_pricing_set]', function(event) {
            if (event.originalEvent !== undefined){
                var selectedOption = $(this).find(':selected');
                if (selectedOption.text() !== '---------'){
                    form_ajax_submit(false);
                }
            }
        });

        $(document).ready(function() {
            $('.tooltip').tooltipster({
                animation: 'swing',
                delay: 200,
                maxWidth: 250,
                theme: 'tooltipster-light'
            });
        });

    })(django.jQuery);
}
