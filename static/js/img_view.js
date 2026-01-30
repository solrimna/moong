console.log("---------- img_view.js 파일 로드 시작");

// 이미지 클릭시 -> 이미지 별도 화면 띄움
function openImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.classList.add('active');
    modalImg.src = imageSrc;
}

// 이미지 클릭시 -> 닫기
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

// 🔥 공통 이미지 미리보기 함수
function handleImagePreview(file, previewElement, isMultiple = false) {
    if (!file.type.startsWith('image/')) {
        alert('이미지 파일만 선택해주세요! (JPG, PNG)');
        return;
    }
    
    const reader = new FileReader();
    
    reader.onload = function(event) {
        const img = document.createElement('img');
        img.src = event.target.result;
        
        if (isMultiple) {
            // 다중 이미지 (게시글용) - 추가
            previewElement.appendChild(img);
        } else {
            // 단일 이미지 (프로필용) - 교체
            if (previewElement.tagName === 'IMG') {
                previewElement.src = event.target.result;
            } else {
                img.alt = '프로필 미리보기';
                img.className = 'current-image';
                img.id = previewElement.id;
                previewElement.parentNode.replaceChild(img, previewElement);
            }
        }
    };
    
    reader.readAsDataURL(file);
}

// 이미지 등록 -> 미리보기 동작
document.addEventListener('DOMContentLoaded', function() {
    // 1. 다중 이미지 미리보기 (게시글용)
    const imagesInput = document.getElementById('images');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imagesInput && imagePreview) {
        console.log("다중 이미지 요소 찾음, 이벤트 등록");
        
        imagesInput.addEventListener('change', function(e) {
            const files = e.target.files;
            
            // 최대 5개 제한
            if (files.length > 5) {
                alert('이미지는 최대 5개까지 업로드 가능합니다.');
                e.target.value = '';
                return;
            }
            
            // 기존 미리보기 초기화
            imagePreview.innerHTML = '';
            
            // 각 파일 처리
            for (let i = 0; i < files.length; i++) {
                handleImagePreview(files[i], imagePreview, true);
            }
        });
    }
    
    // 2. 단일 이미지 미리보기 (프로필용)
    const profileInput = document.getElementById('profileImageInput');
    const profilePreview = document.getElementById('profilePreview');
    
    if (profileInput && profilePreview) {
        console.log("단일 이미지 요소 찾음, 이벤트 등록");
        
        profileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleImagePreview(file, profilePreview, false);
            }
        });
    }
});