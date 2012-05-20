

$(window).load(function() {
    var x = $('.navbar-fixed-top-plus').offset().top + $('.navbar-fixed-top-plus').outerHeight();
    $('body').css('padding-top', x + 10 + 'px');
});

$(document).ready( function() {
    $('.autoresize').autoResize();
    $('body').tooltip({selector : ":input"});
    $('#title').focus();
    
    $('.alert').delay(3000).fadeOut('slow');
    
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
        var help = $(this).parent().find('.help-inline');
        
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
            help.addClass('help-overflown');
            $(this).addClass('input-overflown');
        } else {
            help_warning.html('left');
            help.removeClass('help-overflown');
            $(this).removeClass('input-overflown');
        }
        
        help_count.html(Math.abs(limit - count));
    });
    
    $('.word_limited, .char_limited').trigger('keyup');
});
  