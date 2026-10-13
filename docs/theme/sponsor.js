// Adds a Sponsor icon to the header bar, beside print / repository / edit.
//
// Done in JS rather than by overriding index.hbs: the template would have to be
// vendored into theme/ and kept in step with every mdBook upgrade, for one
// anchor. The icon mirrors mdBook's own markup — an <a> wrapping a
// <span class="fa-svg"> with an inline SVG — so it inherits the existing
// hover and theme styling with no extra CSS.
(function () {
    "use strict";

    // Font Awesome Free 6.2.0 "heart" (CC BY 4.0), matching the bundled icons.
    var HEART =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" aria-hidden="true">' +
        '<path d="M47.6 300.4L228.3 469.1c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9' +
        'L464.4 300.4c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141' +
        'C347 36.5 300.6 51.4 268 84L256 96 244 84c-32.6-32.6-79-47.5-124.6-39.9' +
        'C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"/></svg>';

    function addSponsorButton() {
        var bar = document.querySelector(".right-buttons");
        if (!bar || document.getElementById("sponsor-button")) {
            return;
        }

        var root = typeof path_to_root === "string" ? path_to_root : "";
        var link = document.createElement("a");
        link.href = root + "support.html";
        link.title = "Sponsor / commercial support";
        link.setAttribute("aria-label", "Sponsor / commercial support");

        var icon = document.createElement("span");
        icon.className = "fa-svg";
        icon.id = "sponsor-button";
        icon.innerHTML = HEART;

        link.appendChild(icon);
        bar.appendChild(link);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", addSponsorButton);
    } else {
        addSponsorButton();
    }
})();
