const PARTIALLY_SAVED = 1;   
const SAVED = 2;             
const NOT_SAVED = 3
const UNKNOWN_FIELD = 4


//401 Unauthorized - No valid API key provided.
//402 Request Failed - Parameters were valid but request failed.
//404 Not Found - The requested item doesn't exist.
//500, 502, 503, 504 Server errors - something went wrong on Stripe's end.

$(window).load(function() {
    var x = $('.navbar-fixed-top-plus').offset().top + $('.navbar-fixed-top-plus').outerHeight();
    $('body').css('padding-top', x + 10 + 'px');
});

$(document).ready( function() {
    $('.autoresize').autoResize();
    $('body').tooltip({selector : ":input"});
    $('#title').focus();
    
    $('.alert').delay(3000).fadeOut('slow');
    
    var private_link = $('#private_link > a').attr('href');
    $('#private_link > a').attr('href', 'http://' + window.location.host + '/' + private_link);
    $('#private_link > a').html(window.location.host + '/' + private_link);
    
    var public_link = $('#public_link > a').attr('href');
    $('#public_link > a').attr('href', 'http://' + window.location.host + '/' + public_link);
    $('#public_link > a').html(window.location.host + '/' + public_link);
    
    $('#private').addClass('active');
    $('#private_link').css({'display' : 'block'});
    
    $.each($('.navbar-inner .btn-success'), function(index, value) {
        var parent_link = $(this).parent().attr('href');
        var pathname = window.location.pathname; 
        var button = $(this);
        
        if (pathname == parent_link) {
            $(this).parent().replaceWith(button);
            button.removeClass('btn-success');
            button.addClass('disabled');
        }
    });
    
    setInterval(function() {
        var kvs = {};
        var size = 0;
        
        $.each($('.word_limited, .char_limited'), function(index, value) {
            if ($(this).hasClass('input-changed') && !$(this).hasClass('input-overflown')) {
                kvs[$(this).attr('id')] = $(this).val();
                size++;
            }
        });
        
        if (size == 0) return;
        
        $('#form_status').html('Saving...');
        var kvs = JSON.stringify(kvs);
        
        $.ajax({
            type: 'POST',
            url: "/api/v1/pitch" + window.location.pathname,
            data: kvs,
            dataType: "json",
            contentType: "application/json; charset=utf-8"
        }).done(function(data, code, jqxhr) {
            var code = data['code'];
            var message = data['message'];
            var feedback; 
            
            if (code == PARTIALLY_SAVED || code == SAVED) {
                feedback = 'All changes saved<span id="saved_ago"></span>.'
            } else {
                feedback = 'An unknown error has occured.'
            }
            
            if ($('.input-overflown').length > 0) {
                feedback = feedback + ' Be sure to correct other fields.';
            }
            
            $('.word_limited, .char_limited').removeClass('input-changed');
            setTimeout(function() {$('#form_status').html(feedback);}, 400);
            
        }).fail(function(jqxhr, code, exception) {
            // TODO: Error handling
            $('#form_status').html('A ' + jqxhr.status + ' error occured while saving.');
        });
        
    }, 5000);
    
    $('#private').click(function() {
        event.preventDefault();
        $(this).addClass('active');
        $('#private_link').css({'display' : 'block'});
        $('#public').removeClass('active');
        $('#public_link').css({'display' : 'none'});
        $('#private_check').attr('checked', 'checked');
    });
    
    $('#public').click(function() {
        event.preventDefault();
        $(this).addClass('active');
        $('#public_link').css({'display' : 'block'});
        $('#private').removeClass('active');
        $('#private_link').css({'display' : 'none'});
        $('#private_check').removeAttr('checked');
    });
    
    $('#title').keyup(function() {
        var title = $(this).val().substring(0,17);
        
        
        if($(this).val().length >= 17) {
            $('button[class*="disabled"]').html(title + '...');
        } else {
            $('button[class*="disabled"]').html(title);
        }
        
        // move down the body if we have to
        var x = $('.navbar-fixed-top-plus').offset().top + $('.navbar-fixed-top-plus').outerHeight();
        $('body').css('padding-top', x + 10 + 'px');
    });
    
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
            $(this).addClass('input-changed');
        }
        
        help_count.html(Math.abs(limit - count));
    });
    
    //initial run through
    $.each($('.word_limited, .char_limited'), function() {
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
});
 
