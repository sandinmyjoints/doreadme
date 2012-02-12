/* Author:

 */

$(document).ready(function () {
//    $("div.story").hover(function (event) {
    $("div.day").hover(function (event) {
//            $(this).find("a.full_story").css("opacity", 1);
            $(this).find("a.full_story").css("color", "#069");
        },
        function (event) {
//            $(this).find("a.full_story").css("opacity", .2);
            $(this).find("a.full_story").css("color", "#888");
        });

    $("a.contact_form_link").click(function (event) {
        event.preventDefault();
        $send_button = $("div#contact_form input[type='submit']").hide();
        $("div#contact_form").dialog({
            modal:true,
            title:"Contact us",
            buttons:{
                "Cancel":function () {
                    $(this).dialog("close");
                },
                "Send":function () {
                    $send_button.click();
                }
            }

        });
    });
});






