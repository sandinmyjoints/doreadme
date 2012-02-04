/* Author:

 */

$(document).ready(function () {
    $("p.teaser").hover(function (event) {
            $(this).find("a.full_story").css("opacity", 1);
        },
        function (event) {
            $(this).find("a.full_story").css("opacity", .2);
        });
});






