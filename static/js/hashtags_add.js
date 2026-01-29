document.getElementById('add-tag-btn').addEventListener('click', function() {
    const input = document.getElementById('direct-tag-input');
    let tagValue = input.value.trim();

    if (tagValue) {
        // '#' 문자가 있으면 제거 (서버에서 일괄 처리하기 위함)
        tagValue = tagValue.replace(/^#/, '');

        const container = document.getElementById('tag-container');
        
        // 새로운 태그를 HTML 구조로 생성
        const newTag = `
            <label style="display: inline-block; margin: 5px; padding: 8px 12px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 20px;">
                <input type="checkbox" name="tags" value="${tagValue}" checked>
                #${tagValue}
            </label>
        `;
        
        // 컨테이너에 추가
        container.insertAdjacentHTML('beforeend', newTag);
        
        // 입력창 초기화
        input.value = '';
        input.focus();
    } else {
        alert('태그 내용을 입력해주세요.');
    }
});

// 엔터키로도 추가 가능하게 만들기
document.getElementById('direct-tag-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // 폼 제출 방지
        document.getElementById('add-tag-btn').click();
    }
});