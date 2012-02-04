/* Author:

 */

$(document).ready(function () {
    $("article").hover(function (event) {
//            $(this).find("a.full_story").css("opacity", 1);
            $(this).find("a.full_story").css("color", "#333");
        },
        function (event) {
//            $(this).find("a.full_story").css("opacity", .2);
            $(this).find("a.full_story").css("color", "#AAA");
        });

    $("a.contact_form_link").click(function(event) {
        event.preventDefault();
        $("div#contact_form").dialog();
    });
});






