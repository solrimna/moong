document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tap-slider').forEach(function (slider) {
        var slides = slider.querySelectorAll('.tap-slide');
        var dots = slider.querySelectorAll('.tap-dot');
        var prev = slider.querySelector('.tap-prev');
        var next = slider.querySelector('.tap-next');
        var current = 0;

        function goTo(index) {
            if (index < 0) index = slides.length - 1;
            if (index >= slides.length) index = 0;
            current = index;
            slides.forEach(function (s, i) {
                s.classList.toggle('active', i === current);
            });
            dots.forEach(function (d, i) {
                d.classList.toggle('active', i === current);
            });
        }

        if (prev) prev.addEventListener('click', function () { goTo(current - 1); });
        if (next) next.addEventListener('click', function () { goTo(current + 1); });
    });
});
