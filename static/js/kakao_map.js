(function() {
    var KAKAO_APP_KEY = '480058f96b58da4bae7e2e8ae398a476';

    function renderMaps() {
        var mapElements = document.querySelectorAll('[data-kakao-address]');
        if (mapElements.length === 0) return;

        var script = document.createElement('script');
        script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=' + KAKAO_APP_KEY + '&autoload=false&libraries=services';
        script.onload = function() {
            kakao.maps.load(function() {
                mapElements.forEach(function(el) {
                    var address = el.dataset.kakaoAddress;
                    var places = new kakao.maps.services.Places();
                    places.keywordSearch(address, function(result, status) {
                        if (status === kakao.maps.services.Status.OK) {
                            var coords = new kakao.maps.LatLng(result[0].y, result[0].x);
                            var map = new kakao.maps.Map(el, {
                                center: coords,
                                level: 5
                            });
                            new kakao.maps.Marker({ map: map, position: coords });
                        } else {
                            el.style.display = 'none';
                        }
                    });
                });
            });
        };
        document.head.appendChild(script);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderMaps);
    } else {
        renderMaps();
    }
})();
