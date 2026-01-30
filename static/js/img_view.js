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
    } else {
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
    }
    
    // 🔥 프로필 이미지 미리보기 기능 추가
    const profileInput = document.getElementById('profileImageInput');
    const profilePreview = document.getElementById('profilePreview');
    
    if (!profileInput || !profilePreview) {
        console.log("이 페이지에는 profileImageInput 요소가 없음");
    } else {
        console.log("프로필 이미지 요소 찾음, 이벤트 등록 시작");
        
        profileInput.addEventListener('change', function(e) {
            console.log("---------- 프로필 이미지 변경 이벤트 발생");
            const file = e.target.files[0];
            
            if (file) {
                console.log("선택된 파일:", file.name);
                
                // 파일이 이미지인지 확인
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {
                        console.log("이미지 로드 완료, 미리보기 업데이트");
                        
                        // 기존 요소가 img 태그인지 div(placeholder)인지 확인
                        if (profilePreview.tagName === 'IMG') {
                            // 이미 이미지면 src만 변경
                            profilePreview.src = event.target.result;
                        } else {
                            // placeholder였으면 img로 교체
                            const newImg = document.createElement('img');
                            newImg.src = event.target.result;
                            newImg.alt = '프로필 미리보기';
                            newImg.className = 'current-image';
                            newImg.id = 'profilePreview';
                            profilePreview.parentNode.replaceChild(newImg, profilePreview);
                        }
                    };
                    
                    reader.readAsDataURL(file);
                } else {
                    alert('이미지 파일만 선택해주세요! (JPG, PNG)');
                }
            }
        });
        
        console.log("프로필 이미지 이벤트 리스너 등록 완료");
    }
});