


$(document).ready(function () {
    /// First slider Jquery
    $('#owl-demo').owlCarousel({
        items: 4,
        loop: true,
        nav: false,
        /*navText: ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],*/
        dots: false,
        autoplay: true,
        autoplaySpeed: 1500,
        smartSpeed: 250,
        autoplayHoverPause: false,
        /*animateOut: 'fadeOut',
        animateIn: 'fadeIn',*/

        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            1000: {
                items: 1
            }
        }
    });
});