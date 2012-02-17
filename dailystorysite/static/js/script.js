/* Author:

 */

$(document).ready(function () {
//    $("div.story").hover(function (event) {
    $("div.day").hover(function (event) {
            $(this).find("a.full_story").css("color", "#069");
        },
        function (event) {
            $(this).find("a.full_story").css("color", "#333");
        });

    var $contact_form_div = $("div#contact_form");
    var $form = $contact_form_div.find("form");

    var $contact_dialog = $("div#contact_form").dialog({
        resizable:false,
        autoOpen:false,
        animate:true,
        animateEasing:"swing",
        show:"fade",
        hide:"fade",
        width:"auto",
        height:"auto",
        modal:true,
        title:"Contact us",
        close:function (event, ui) {
            $(this).dialog("destroy");
        },
        buttons:{
            "Cancel":function () {
                $(this).dialog("close");
            },
            "Send":function () {
                $.ajax($form.attr("action"),
//                $.ajax($(this).find("form").attr("action"),
                    {
                        type:"POST",
                        dataType:"json",
                        data:{
                            'name':$form.find("input#id_name").val(),
//                            'name':$(this).find("form").find("input#id_name").val(),
                            'email':$form.find("input#id_email").val(),
//                            'email':$(this).find("form").find("input#id_email").val(),
                            'body':$form.find("textarea#id_body").val()
//                            'body':$(this).find("form").find("textarea#id_body").val()
                        },
                        error:function (jqXHR, textStatus, errorThrown) {
                            $contact_form_div.html("Sorry, we weren't able to send your message. Please try again.");
//                            $(this).html("Sorry, we weren't able to send your message. Please try again.");

                        },
                        success:function (data, textStatus, jqXHR) {
                            if (!data.error) {
                                $contact_form_div.find("input[type=submit], input[type=button]").hide(); // the dialog box wil provide the buttons
                                $contact_form_div.html("<p>" + data.message + "</p>");
                                $contact_form_div.dialog("option", "buttons",
                                    {
                                        "Close":function () {
                                            $(this).dialog("close");
                                        }
                                    });
                            }
                            else {
                                $contact_form_div.find("span.error").remove();
                                if (data.data.name) {
                                    $("#id_name").prevUntil("li").before("<span class='error'>" + data.data.name + "</span>");
                                }
                                if (data.data.email) {
                                    $("#id_email").prevUntil("li").before("<span class='error'>" + data.data.email + "</span>");
                                }
                                if (data.data.body) {
                                    $("#id_body").prevUntil("li").before("<span class='error'>" + data.data.body + "</span>");
                                }
                            }
                        },
                        complete:function (jqXHR, textStatus) {
                            $form.find("input[type=submit], input[type=button]").hide();  // the dialog box wil provide the buttons
                        }
                    }
                );
            }
        }
    });

    $("a.contact_form_link").live("click", function (event) {
        event.preventDefault();
        $form.find("input[type=submit], input[type=button]").hide();  // the dialog box wil provide the buttons
        $contact_dialog.dialog("open");

    });
});

$(document).ajaxSend(function (event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});



