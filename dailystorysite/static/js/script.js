/* Author:

 */

function create_dialog($elem) {
    var $form = $elem.find("form");
    $form.find("input[type=submit], input[type=button]").hide();  // the dialog box wil provide the buttons

    $elem.dialog({
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
//            $(this).dialog("destroy");
//            $(this).dialog().remove();
        },
        buttons:{
            "Cancel":function () {
                $(this).dialog("close");
            },
            "Send":function () {
                $elem.dialog("option", "disabled", true);
                $elem.spinner({
                    position:'center',
                    height:32,
                    width:32,
                    img:STATIC_URL + "images/spinner_big.gif"
                });
                $.ajax($form.attr("action"),
                    {
                        type:"POST",
                        dataType:"json",
                        data:{
                            'name':$form.find("input#id_name").val(),
                            'email':$form.find("input#id_email").val(),
                            'body':$form.find("textarea#id_body").val()
                        },
                        error:function (jqXHR, textStatus, errorThrown) {
                            $elem.html("Sorry, we weren't able to send your message. Please try again.");
                        },
                        success:function (data, textStatus, jqXHR) {
                            if (!data.error) {
                                $elem.html("<p>" + data.message + "</p>");
                                $elem.dialog("option", "buttons",
                                    {
                                        "Close":function () {
                                            $(this).dialog("close");
                                        }
                                    });
                            }
                            else {
                                $elem.find("span.error").remove();
                                if (data.data.name) {
                                    $elem.find("#id_name").prevUntil("li").before("<span class='error'>" + data.data.name + "</span>");
                                }
                                if (data.data.email) {
                                    $elem.find("#id_email").prevUntil("li").before("<span class='error'>" + data.data.email + "</span>");
                                }
                                if (data.data.body) {
                                    $elem.find("#id_body").prevUntil("li").before("<span class='error'>" + data.data.body + "</span>");
                                }
                            }
                        },
                        complete:function (jqXHR, textStatus) {
                            $elem.spinner('remove');
                            $elem.dialog("option", "disabled", false);
                            $form.find("input[type=submit], input[type=button]").hide();  // the dialog box wil provide the buttons
                        }
                    }
                );
            }
        }
    });
    return $elem.dialog();
}

$(document).ready(function () {
    $("div.day").hover(function (event) {
            $(this).find("a.full_story").css("color", "#069");
        },
        function (event) {
            $(this).find("a.full_story").css("color", "#333");
        });

    $(".additional, .more_actions").hide();

    var $contact_form_div = $("#contact_form_hider div#contact_form");
    var $contact_dialog = create_dialog($contact_form_div);

    $("a.contact_form_link").live("click", function (event) {
        event.preventDefault();
        $contact_dialog.dialog("open");
    });

    $("#calendar-widget").datepicker({
            minDate:-20,
            maxDate:0,
            showOtherMonths:true,
            selectOtherMonths:true,
            onSelect:function (dateText, inst) {
                var day = new Date(dateText);
                window.location = DAY_REDIRECT_URL + "?year=" + day.getFullYear() + "&month=" + (day.getMonth() + 1) + "&day=" + day.getDate();
            }
        }
    );

    $("a.yes, a.no, a.maybe").button();

    $("div.day").each(function(i, elem) {
        var $self=$(this);
        $self.find("a.maybe").on("click", function (event) {
            event.preventDefault();
            $self.find("p.additional").slideToggle(250, "swing");
            $(this).button("option", "disabled", true);
        });

        $self.find("a.no").on("click", function (event) {
            event.preventDefault();
            $self.find("div.more_actions").slideToggle(750, "easeOutBounce");
            $(this).button("option", "disabled", true);
        });
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



