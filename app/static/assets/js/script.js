$(".toggle-password").click(function() {
    $(this).toggleClass("fa-eye fa-eye-slash");
    input = $(this).parent().find("input");
    if (input.attr("type") == "password") {
        input.attr("type", "text");
    } else {
        input.attr("type", "password");
    }
});

$(document).ready(function() { 
    $(window).scroll(function() {
    var theTop = $(window).scrollTop();
        $('.colwrap').css('top', $(window).scrollTop() + 10 + "px");
    });
        
    // this might better with some kind of animate function to make scrolling smoother    
});