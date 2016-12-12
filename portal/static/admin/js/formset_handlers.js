(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        alert("Language row added!")
        if (formsetName == 'author_set') {
            alert("Language row added!")
        }
    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);