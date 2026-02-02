function toggleDdomoong(participationId) {
    const url = DDOMOONG_URL_BASE.replace('/0/', '/' + participationId + '/');
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 또뭉 개수 업데이트
            document.getElementById(`ddo-count-${participationId}`).textContent = 
                `또뭉 ${data.ddo_count}개`;
            
            // 버튼 텍스트 변경
            const btnText = document.getElementById(`ddo-text-${participationId}`);
            if (data.is_ddo) {
                btnText.innerHTML = '❤️ 또뭉 취소';
            } else {
                btnText.innerHTML = '🤍 또뭉 주기';
            }
        } else {
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    });
}
