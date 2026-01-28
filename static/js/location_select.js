// <!-- ===================== -->
// <!-- AJAX 행정구역 JS -->
// <!-- ===================== -->

document.addEventListener("DOMContentLoaded", function () {

    const sidoSelect = document.getElementById("sido");
    const sigunguSelect = document.getElementById("sigungu");
    const eupSelect = document.getElementById("eupmyeondong");

    // 1️⃣ 시/도 로드
    fetch("/locations/sido/")
        .then(res => res.json())
        .then(data => {
                        data.forEach(sido => {
            const opt = document.createElement("option");
            opt.value = sido;
            opt.textContent = sido;
            sidoSelect.appendChild(opt);
                        });
                    })
        .catch(err => {
        console.error("시/도 로드 실패", err);
        });
            
    // 2️⃣ 시/도 변경 → 시/군/구
    sidoSelect.addEventListener("change", function () {
                const sido = this.value;
                
        // 하위 초기화
        sigunguSelect.innerHTML = `<option value="">시/군/구 선택</option>`;
        eupSelect.innerHTML = `<option value="">읍/면/동 선택</option>`;
                
        if (!sido) return;

                    fetch(`/locations/sigungu/?sido=${encodeURIComponent(sido)}`)
        .then(res => res.json())
                        .then(data => {
                            data.forEach(sigungu => {
            const opt = document.createElement("option");
            opt.value = sigungu;
            opt.textContent = sigungu;
            sigunguSelect.appendChild(opt);
                            });
                        })
        .catch(err => {
            console.error("시/군/구 로드 실패", err);
        });
            });
            
    // 3️⃣ 시/군/구 변경 → 읍/면/동
    sigunguSelect.addEventListener("change", function () {
                const sigungu = this.value;
        const sido = sidoSelect.value;
                
        eupSelect.innerHTML = `<option value="">읍/면/동 선택</option>`;
                
        if (!sido || !sigungu) return;

        fetch(
        `/locations/eupmyeondong/?sido=${encodeURIComponent(sido)}&sigungu=${encodeURIComponent(sigungu)}`
        )
        .then(res => res.json())
                        .then(data => {
            console.log("받은 데이터:", data);

            data.forEach(obj => {
                console.log("추가하는 option:", obj.id, obj.name);
                const opt = document.createElement("option");
                opt.value = obj.id;       // ⭐ Location.id
                opt.textContent = obj.name;
                eupSelect.appendChild(opt);
                            });
                        })
        .catch(err => {
            console.error("읍/면/동 로드 실패", err);
        });
    });

});

