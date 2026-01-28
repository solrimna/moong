console.log("---------- img_view.js 파일 로드 시작");

// 이미지 클릭시 -> 이미지 별도 화면 띄움
function openImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.classList.add('active');
    modalImg.src = imageSrc;
}
// 이미지 클릭시 -> 닫기(클릭 이후 동작)
function closeImageModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('active');
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeImageModal();
    }
});

// 이미지 등록 -> 미리보기 동작
document.addEventListener('DOMContentLoaded', function() {
    const imagesInput = document.getElementById('images');
    const imagePreview = document.getElementById('imagePreview');
    
    // ⭐ 요소가 없으면 종료 (다른 페이지에서 실행될 때)
    if (!imagesInput || !imagePreview) {
        console.log("이 페이지에는 images 요소가 없음");
        return;
    }
    
    console.log("images 요소 찾음, 이벤트 등록 시작");
    
    // 이벤트 리스너 등록
    imagesInput.addEventListener('change', function(e) {
        console.log("---------- 이벤트 발생");
        const preview = document.getElementById('imagePreview');
        preview.innerHTML = ''; // 기존 미리보기 초기화
        
        const files = e.target.files;
        
        console.log("선택된 파일 개수:", files.length); 
        for (let i = 0; i < files.length; i++) {
            console.log(`파일 ${i}:`, files[i].name);
        }

        // 최대 5개 제한
        if (files.length > 5) {
            alert('이미지는 최대 5개까지 업로드 가능합니다.');
            e.target.value = ''; // 선택 취소
            return;
        }
        
        // 미리보기 생성
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // 이미지 파일인지 확인
            if (!file.type.startsWith('image/')) {
                continue;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                preview.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });
    
    console.log("이벤트 리스너 등록 완료");
});