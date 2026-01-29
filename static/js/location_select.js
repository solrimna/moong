// <!-- ===================== -->
// <!-- AJAX 행정구역 JS -->
// <!-- ===================== -->
console.log("---------- location_select.js 파일 로드 시작");

document.addEventListener("DOMContentLoaded", function () {

    const sidoSelect = document.getElementById("sido");
    const sigunguSelect = document.getElementById("sigungu");
    const eupSelect = document.getElementById("eupmyeondong");

    const savedLocationElem = document.getElementById("saved_location");

    const savedSido = savedLocationElem?.dataset?.sido ?? "";
    const savedSigungu = savedLocationElem?.dataset?.sigungu ?? "";
    const savedLocationId = savedLocationElem?.dataset?.locationId ?? null;

    console.log("저장된 정보 확인 : ", savedSido, savedSigungu);
    console.log("저장된 정보 확인 id : ", savedLocationId);

    // 1️⃣ 시/도 로드
    fetch("/locations/sido/")
        .then(res => res.json())
        .then(data => {
            data.forEach(sido => {
                const opt = document.createElement("option");
                opt.value = sido;
                opt.textContent = sido;
                if (sido === savedSido) {
                    console.log("시도 데이터 확인 ", sido, savedSido);
                    opt.selected = true;
                }
                console.log("시도 데이터 확인 ", sido, savedSido);
                sidoSelect.appendChild(opt);
            });

            // 현재 시/도가 선택되어 있으면 시/군/구 로드
            if (savedSido) {
                sidoSelect.dispatchEvent(new Event('change'));
            }
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
                    if (sigungu === savedSigungu) {
                        opt.selected = true;
                    }
                    sigunguSelect.appendChild(opt);
                });

                // 현재 시/군/구가 선택되어 있으면 읍/면/동 로드
                if (savedSigungu && sido === savedSido) {
                    sigunguSelect.dispatchEvent(new Event('change'));
                }
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
                    if (obj.id == savedLocationId) {
                        opt.selected = true;
                    }
                    eupSelect.appendChild(opt);
                });
            })
            .catch(err => {
                console.error("읍/면/동 로드 실패", err);
            });
    });

});