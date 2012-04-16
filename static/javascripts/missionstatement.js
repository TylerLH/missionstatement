$(document).ready( function() {
    $('.autoresize').autoResize();
    $('#body').tooltip({selector : ":input"});
    $('#title').focus();
    
    $('.word_limited, .char_limited').keyup(function() {
        
        if ($(this).parents('arclones').length > 0) {
            return;
        }
        
        var contents = $(this).val();
        var count_words = $(this).hasClass('word_limited');
        var limit = $(this).attr('size');
        var help_count = $(this).parent().find('.units-left');
        var help_plural = $(this).parent().find('.plural');
        var help_warning = $(this).parent().find('.too-much');
        
        if (count_words) {
            var count = contents == "" ? 0 : contents.trim().split(' ').length
        } else {
            var count = contents.length
        }
        
        if (Math.abs(count - limit) == 1) {
            help_plural.html('');
        } else {
            help_plural.html('s');
        }
        
        if (count > limit) {
            help_warning.html('too many');
        } else {
            help_warning.html('left');
        }
        
        help_count.html(Math.abs(limit - count));
    });
    
    $('.word_limited, .char_limited').trigger('keyup');
});
  